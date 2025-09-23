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
    clubs = M2M(LazyTableReference("PlayerToClub", module_path=__name__))
    bets = M2M(LazyTableReference("Bet", module_path=__name__))


class Track(Table):
    """
    A TrackMania track/map
    """
    uuid = UUID(unique=True)
    name = Varchar()
    clubs = M2M(LazyTableReference("TrackToClub", module_path=__name__))


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
    club = ForeignKey(Club, null=False)
    # 0: versus, 1: guess the time, 2: raffle
    type = SmallInt()
    # when the window to perform bets on this prediction closes
    closes_at = Timestamp()
    # when the prediction ends and results are computed
    ends_at = Timestamp()
    # set to true when the points are distributed
    processed = Boolean()
    # players whose results on the track decide the outcome of the prediction
    # in case of raffles, all players that join the raffle are added as a protagonist
    protagonists = M2M(LazyTableReference(
        "PlayerToPrediction", module_path=__name__))
    bets = M2M(LazyTableReference("Bet", module_path=__name__))

    async def get_records(self):
        """
        Returns the earliest records present in the database that have been uploaded after the end of this prediction,
        useful to check prediction results with correct data.
        Note: if the results are empty, it does not mean that the player(s) don't have records on the given
        track, just that the records are not yet uploaded here (so a call to Nadeo services needs to be performed).
        """
        protagonists = await self.get_m2m(self.protagonists)
        return asyncio.gather(*[TrackmaniaRecord.get_first_created_after_timestamp(
            player=p.id,
            track=self.track.id,
            ts=self.ends_at
        ).run() for p in protagonists]) 


class PlayerToPrediction(Table):
    """
    Relationship that tells which players are the protagonists / topic of each prediction
    """
    player = ForeignKey(Player)
    prediction = ForeignKey(Prediction)
    # value to be filled when the prediction expires
    result = Integer()
    player_prediction_constraint = UniqueConstraint(["player", "prediction"])


class Bet(Table):
    """
    Relationship that tells which player is betting on which prediction
    """
    player = ForeignKey(Player)
    prediction = ForeignKey(Prediction)
    # which outcome has the player betted on
    outcome = Integer()
    # how many points have been bet
    points = Integer()
    bet_constraint = UniqueConstraint(["player", "prediction"])


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