from piccolo.table import Table
from piccolo.columns import *
from piccolo.columns.m2m import M2M
from datetime import timedelta, datetime
from piccolo.constraint import UniqueConstraint
import asyncio

STARTING_POINTS = 1000

class Player(Table):
    """
    TrackMania player
    """
    uuid = UUID(unique=True)
    name = Varchar()
    # used for authentication through OpenPlanet
    secret = Varchar(64, unique=True)
    tracks = M2M(LazyTableReference("PlayerToTrack", module_path=__name__))
    clubs = M2M(LazyTableReference("PlayerToClub", module_path=__name__))


class Track(Table):
    """
    A TrackMania track/map
    """
    uuid = UUID(unique=True)
    name = Varchar()
    players = M2M(LazyTableReference("PlayerToTrack", module_path=__name__))
    clubs = M2M(LazyTableReference("TrackToClub", module_path=__name__))


class PlayerToTrack(Table):
    """
    Relationship table for allowing players to claim points for spending time on tracks.
    NOTE: this is different from "TrackmaniaRecord", because we need an unique constraint here, and this tracks
    when a map was last played, outside of personal bests.
    """
    player = ForeignKey(Player)
    track = ForeignKey(Track)
    last_played_at = Timestamp()
    player_track_constraint = UniqueConstraint(["player", "track"])

    @classmethod
    def get_last_played(cls, player, track):
        return cls.select(cls.last_played_at).where((cls.player == player) & (cls.track == track))


class TrackmaniaRecord(Table):
    """
    Table to store TM records with useful metadata
    """
    player = ForeignKey(Player)
    track = ForeignKey(Track)
    time = Integer()
    # when this record was uploaded to nadeo servers
    nadeo_timestamp = Timestamp()
    # when this record was uploaded to this table
    created_at = Timestamp()
    # stores which entity used Nadeo online services to check the player's time
    # since api calls to the Nadeo Services are rate limited, to avoid clogging the prediction monitor clients
    # can send this information to the server using their own token
    checked_by = Varchar(null=True)

    @classmethod
    def get_first_created_after_timestamp(cls, player, track, ts: datetime):
        """
        Query that returns the earliest record in the table after a given timestamp
        """
        return cls.select().where(
            (cls.player == player) &
            (cls.track == track) &
            (cls.created_at > ts)
        ).order_by(cls.created_at).first()


class Club(Table):
    """
    Club of players
    """
    name = Varchar(unique=True)
    # todo add password maybe?
    players = M2M(LazyTableReference("PlayerToClub", module_path=__name__))
    tracks = M2M(LazyTableReference("TrackToClub", module_path=__name__))
    # can be used to set custom name for the club points
    points_name = Varchar(default="points")
    # 0: everyone allowed to make predictions, 1: only admins
    restricted = Boolean()
    # 0: hidden, 1: public
    visibility = Boolean()
    # number of automated predictions to be created periodically
    automated_amount = SmallInt(default=2)
    # frequency at which automated predictions are performed
    automated_frequency = Interval(default=timedelta(minutes=30))
    # interval for which predictions are open
    automated_open = Interval(default=timedelta(minutes=5))
    # when to check for prediction results after it's created
    automated_end = Interval(default=timedelta(hours=6))


class PlayerToClub(Table):
    """
    Relationship table for players that are part of clubs
    """
    player = ForeignKey(Player)
    club = ForeignKey(Club)
    points = Integer(default=STARTING_POINTS)
    admin = Boolean()
    player_club_constraint = UniqueConstraint(["player", "club"])

    @classmethod
    async def give_points(cls, player, club, points):
        row = await cls.objects().get(
            (cls.player == player) & (cls.club == club)
        )
        await row.update_self({row.points: row.points + points})


class TrackToClub(Table):
    """
    Relationship table for tracks that belong into a club
    """
    track = ForeignKey(Track)
    club = ForeignKey(Club)
    # amount of predictions ran on this track
    counter = Integer()
    track_club_constraint = UniqueConstraint(["track", "club"])


class Prediction(Table):
    """
    Twitch-style predictions on TrackMania tracks
    """
    track = ForeignKey(Track)
    club = ForeignKey(Club)
    # 0: versus, 1: guess the time, 2: raffle
    type = SmallInt()
    # amount of points to give in order to enter this prediction
    # NOTE: for raffles, this just indicates the payout to give to the winner
    entry_fee = Integer()
    # when the window to perform bets on this prediction closes
    created_at = Timestamp()
    # when the prediction ends and results are computed
    ends_at = Timestamp()
    # set to true when the points are distributed
    processed = Boolean()
    # players whose results on the track decide the outcome of the prediction
    protagonists = M2M(LazyTableReference("PlayerToPrediction", module_path=__name__))

    async def get_records(self, protagonists=None):
        """
        Returns the earliest records present in the database that have been uploaded after the end of this prediction,
        useful to check prediction results with correct data.
        Note: if the results are empty, it does not mean that the player(s) don't have records on the given
        track, just that the records are not yet uploaded here (so a call to Nadeo services needs to be performed).
        """
        if not protagonists:
            protagonists = await self.get_m2m(self.protagonists)
        return await asyncio.gather(*[TrackmaniaRecord.get_first_created_after_timestamp(
            player=p.id,
            track=self.track.id,
            ts=self.ends_at
        ) for p in protagonists])
    
    def get_bets(self):
        """
        Gets all bets related to this prediction
        """
        return Bet.objects(Bet.player).where(Bet.prediction == self.id)
    
    @classmethod
    async def get_club_predictions(cls, club_id, hours=0):
        """
        Gets all active predictions in a given club
        """
        out = []
        # gets active predictions or those that ended at most "hours" ago
        predictions = await cls.objects(cls.track).where(
            (cls.club == club_id) & ((not cls.processed) | (cls.ends_at + timedelta(hours=hours) > datetime.now()))
        )
        protagonists_list = await asyncio.gather(*[
            prediction.get_m2m() for prediction in predictions
        ])
        for prediction, protagonists in zip(predictions, protagonists_list):
            d = prediction.to_dict()
            d["protagonists"] = [protagonist.to_dict() for protagonist in protagonists]
            out.append(d)
        return out

class PlayerToPrediction(Table):
    """
    Relationship that tells which players are the protagonists / topic of each prediction
    """
    player = ForeignKey(Player)
    prediction = ForeignKey(Prediction)
    player_prediction_constraint = UniqueConstraint(["player", "prediction"])


class Bet(Table):
    """
    Relationship that tells which player is betting on which prediction
    """
    player = ForeignKey(Player)
    prediction = ForeignKey(Prediction)
    # which outcome has the player betted on
    outcome = Integer()
    bet_constraint = UniqueConstraint(["player", "prediction"])
