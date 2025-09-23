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
