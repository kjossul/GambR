from piccolo.table import Table
from piccolo.columns import *
from piccolo.columns.m2m import M2M
from datetime import timedelta


class Player(Table):
    """
    TrackMania player
    """
    uuid = UUID(unique=True)
    name = Varchar()
    # used for authentication with OpenPlanet
    secret = Varchar(32)
    groups = M2M(LazyTableReference("PlayerToGroup", module_path=__name__))
    bets = M2M(LazyTableReference("Bet", module_path=__name__))


class Track(Table):
    """
    A TrackMania track/map
    """
    uuid = UUID(unique=True)
    name = Varchar()
    groups = M2M(LazyTableReference("TrackToGroup", module_path=__name__))


class Group(Table):
    """
    Group of players
    """
    name = Varchar(unique=True)
    players = M2M(LazyTableReference("PlayerToGroup", module_path=__name__))
    tracks = M2M(LazyTableReference("TrackToGroup", module_path=__name__))
    # can be used to set custom name for the group points
    points_name = Varchar(default="points")
    # 0: only admins allowed to make predictions, 1: everyone
    permissions = Boolean()
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


class PlayerToGroup(Table):
    """
    Relationship table for players that are part of groups
    """
    player = ForeignKey(Player)
    group = ForeignKey(Group)
    points = Integer()
    admin = Boolean()


class TrackToGroup(Table):
    """
    Relationship table for tracks that belong into a group
    """
    track = ForeignKey(Track)
    group = ForeignKey(Group)


class Prediction(Table):
    """
    Twitch-style predictions on TrackMania tracks
    """
    track = ForeignKey(Track)
    group = ForeignKey(Group, null=False)
    # 0: versus, 1: guess the time, 2: raffle
    type = SmallInt()
    # when the window to perform bets on this prediction closes
    close_time = Timestamp()
    # when the prediction ends and results are computed
    end_time = Timestamp()
    # players whose results on the track decide the outcome of the prediction
    # in case of raffles, all players that join the raffle are added as a protagonist
    protagonists = M2M(LazyTableReference(
        "PlayerToPrediction", module_path=__name__))
    bets = M2M(LazyTableReference("Bet", module_path=__name__))


class PlayerToPrediction(Table):
    """
    Relationship that tells which players are the protagonists / topic of each prediction
    """
    player = ForeignKey(Player)
    prediction = ForeignKey(Prediction)
    # value to be filled when the prediction expires
    result = Integer()


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