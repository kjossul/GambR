from apscheduler.schedulers.background import BlockingScheduler
from .tables import *
from datetime import datetime
from enum import IntEnum
import asyncio
from .nadeo_api import NadeoAPI
from collections import defaultdict
from random import choice


class PredictionType(IntEnum):
    VERSUS = 0
    GUESS = 1
    RAFFLE = 2

class PredictionManager:
    def __init__(self):
        self.nadeo_api = NadeoAPI()
        self.scheduler = BlockingScheduler()
        # todo add nadeo api token initialization

    def start(self, interval_minutes=1):
        self.scheduler.add_job(self.process_expired_predictions, trigger='interval', minutes=interval_minutes)
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    async def create_automated_predictions(self):
        pass

    async def process_expired_predictions(self):
        now = datetime.now()
        queue = await Prediction.objects(Prediction.track).where(
            (Prediction.ends_at < now()) & (not Prediction.processed)
        )
        for prediction in queue:
            bets = await prediction.get_bets()
            distributor = PointsDistributor(prediction, bets)
            records = None
            if prediction.type != PredictionType.RAFFLE:
                protagonists = await prediction.get_m2m(Prediction.protagonists)
                records = await prediction.get_records(protagonists)
                # call nadeo api if no client has yet uploaded valid records for this prediction
                if not records:
                    records = await self.update_records(prediction, protagonists)
                # if nobody improved their time since the prediction was created, the prediction is considered void
                # and all points are returned without modification
                # TODO change this such that it checks just if a player PLAYED the map, not if he improved on it
                # add endpoint to "claim" points for playing a track, with op plugin that tracks playtime
                no_new_records_since_prediction_close = all(record["nadeo_timestamp"] < prediction.created_at for record in records)
                no_playtime_since_prediction_close = all(
                    await PlayerToTrack.get_last_played(player.id, prediction.track) < prediction.created_at for player in protagonists
                )
                if no_new_records_since_prediction_close and no_playtime_since_prediction_close:
                    await distributor.void_prediction()
                    continue
            await distributor.handle_payout(records)


    async def update_records(self, prediction: Prediction, protagonists: list[Player]):
        records = self.nadeo_api.get_records([player.uuid for player in protagonists], prediction.track.uuid)
        now = datetime.now()
        q = TrackmaniaRecord.insert()
        for player, record in zip(protagonists, records):
            record_time = record["recordScore"]["time"]
            ts = datetime.fromisoformat(record["timestamp"])
            r = TrackmaniaRecord(
                player=player.uuid,
                track=prediction.track.uuid,
                time=record_time,
                nadeo_timestamp=ts,
                created_at=now,
            )
            q.add(r)
        # TODO check for nadeo api errors
        return await q.returning(TrackmaniaRecord.all_columns())

class PointsDistributor:
    """
    Class that handles points distribution for predictions.
    NOTE: it assumes each player enters with the same fee
    """
    def __init__(self, prediction: Prediction, bets: list[Bet]):
        self.prediction = prediction
        self.bet_buckets = defaultdict(list)
        self.total_bets = 0
        for bet in bets:
            self.total_bets += 1
            self.bet_buckets[bet.outcome].append(bet)

    async def handle_payout(self, records):
        qs = []
        # amount to be paid to the protagonist of the prediction (incentive for people to play the map)
        # this should only be added if the protagonist set a pb on the map after the prediction window closed
        # NOTE: gets 5% of total bets
        protagonist_bonus = int(self.prediction.entry_fee * self.total_bets * 0.05)
        if self.prediction.type == PredictionType.VERSUS:
            # in this case we just give the points to the players that bet correctly
            fastest_record = min(records, key=lambda r: r["time"])
            fastest_player = fastest_record["player"]
            multiplier = self.total_bets / len(self.bet_buckets[fastest_player])
            # distribute bet points
            for bet in self.bet_buckets[fastest_player]:
                win = int(multiplier * self.prediction.entry_fee)
                qs.append(PlayerToClub.give_points(bet.player.id, self.prediction.club, win))
            # distribute bonus points to bet protagonist if he improved on the map after the prediction was created
            if fastest_record["nadeo_timestamp"] > self.prediction.created_at:
                qs.append(PlayerToClub.give_points(fastest_player, self.prediction.club, protagonist_bonus))
            qs.append(PlayerToClub.give_points(fastest_player, self.prediction.club))
        elif self.prediction.type == PredictionType.GUESS:
            # closest guess to target time wins, shared if multiple guessed the same time
            target = records[0]["time"]
            closest_guess = min(self.bet_buckets.keys(), key=lambda guess: abs(target - guess))
            win = int(self.prediction.entry_fee * self.total_bets / len(self.bet_buckets[closest_guess])) 
            for bet in self.bet_buckets[target]:
                qs.append(PlayerToClub.give_points(bet.player.id, self.prediction.club, win))
            if records[0]["nadeo_timestamp"] > self.prediction.created_at:
                qs.append(PlayerToClub.give_points(records[0]["player"], self.prediction.club, protagonist_bonus))
        elif self.prediction.type == PredictionType.RAFFLE:
            winner = choice(self.bet_buckets[0])
            # in case of raffles, the entry fee field is used to indicate the amount to pay out
            qs.append(PlayerToClub.give_points(winner.player.id, self.prediction.club, self.prediction.entry_fee))

        # marks this prediction as processed so it doesn't get picked up in the future
        self.prediction.processed = True
        qs.append(self.prediction.save())
        await asyncio.gather(*qs)

    async def void_prediction(self):
        """
        Return to everyone their points
        """
        qs = []
        for bets in self.bet_buckets.values():
            for bet in bets:
                qs.append(PlayerToClub.give_points(bet.player.id, self.prediction.club, bet.points))
        self.prediction.processed = True
        qs.append(self.prediction.save())
        await asyncio.gather(*qs)
        

monitor = PredictionManager()