from piccolo.utils.pydantic import create_pydantic_model
from pydantic import BaseModel, field_validator
from .tables import *
from datetime import timedelta

class Auth(BaseModel):
    token: str

PlayerModel = create_pydantic_model(Player, exclude_columns=(Player.secret,))
class PlayerOut(PlayerModel):
    points: int
    admin: bool

TrackModel = create_pydantic_model(Track)

ClubModel = create_pydantic_model(Club)
class ClubUpdate(ClubModel):
    @field_validator('points_name')
    @classmethod
    def ensure_length(cls, s: str):
        if len(s) < 3 or not s.isalnum():
            raise ValueError("Must be at least 3 characters long. Only alphanumeric types allowed.")
        return s
    
    @field_validator('automated_amount')
    @classmethod
    def ensure_max_amount(cls, x):
        if x > 5:
            raise ValueError("You can't have more than 5 automated predictions")
        return x
        
    @field_validator('automated_frequency')
    @classmethod
    def ensure_min_frequency(cls, f):
        if f < timedelta(minutes=30):
            raise ValueError("Frequency must be at least 30 minutes")
        return f
        
    @field_validator('automated_open')
    @classmethod
    def ensure_max_open_window(cls, f):
        if f > timedelta(minutes=10):
            raise ValueError("Predictions can't be open longer than 10 minutes")
        return f
    
    @field_validator('automated_end')
    @classmethod
    def ensure_max_prediciton_end(cls, f):
        if not timedelta(hours=1) <= f <= timedelta(days=1):
            raise ValueError("Predictions can't last longer than a day, and have a minimum duration of 1 hour")
        return f

class ClubOut(ClubModel):
    id: int
    players: list[PlayerOut]
    tracks: list[TrackModel]

TrackmaniaRecordModel = create_pydantic_model(TrackmaniaRecord)
PredictionModel = create_pydantic_model(Prediction)
class PredictionIn(create_pydantic_model(Prediction, exclude_columns=(Prediction.created_at, Prediction.processed))):
    track: int
    protagonists: list[PlayerModel]

    @field_validator('ends_at')
    @classmethod
    def ensure_prediction_window(cls, dt):
        offset_request_time = datetime.now() - timedelta(seconds=10)
        # account for max request delay
        if dt < offset_request_time + timedelta(hours=1) or dt > offset_request_time + timedelta(days=1):
            raise ValueError("Prediction must be open for at least 1 hour and can't last longer than a day")

class PredictionOut(PredictionModel):
    protagonists: list[PlayerModel]

    @classmethod
    def from_dict(cls, **kwargs):
        kwargs["protagonists"] = [PlayerModel(**p) for p in kwargs["protagonists"]]
        return cls(kwargs)