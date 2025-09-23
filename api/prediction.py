from apscheduler.schedulers.background import BlockingScheduler
from .tables import *
from datetime import datetime
from enum import IntEnum
import asyncio
from .nadeo_api import NadeoAPI

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

    async def process_expired_predictions(self):
        now = datetime.now()
        queue = await Prediction.objects(Prediction.track).where(
            (Prediction.ends_at < now()) & (not Prediction.processed)
        )
        for prediction in queue:
            records = await prediction.get_records()
            if not records:
                self.update_records(prediction)
            if prediction.type == PredictionType.VERSUS:
                pass
            elif prediction.type == PredictionType.GUESS:
                pass
            elif prediction.type == PredictionType.RAFFLE:
                pass # todo not implemented

    async def distribute_points(self, prediction: Prediction):
        pass

    async def update_records(self, prediction: Prediction):
        players = await prediction.get_m2m(Prediction.protagonists)
        records = self.nadeo_api.get_records([player.uuid for player in players], prediction.track.uuid)
        now = datetime.now()
        q = TrackmaniaRecord.insert()
        for player, record in zip(players, records):
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
        await q
        

monitor = PredictionManager()