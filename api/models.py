from piccolo.table import Table
from piccolo.columns import *
from piccolo.columns.m2m import M2M
from datetime import timedelta
from piccolo.constraint import UniqueConstraint

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