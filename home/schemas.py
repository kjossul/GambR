from piccolo.utils.pydantic import create_pydantic_model
from pydantic import BaseModel
from models import *

class Auth(BaseModel):
    token: str

PlayerModel = create_pydantic_model(Player, exclude_columns=(Player.secret,))
class PlayerOut(PlayerModel):
    points: int
    admin: bool

TrackModel = create_pydantic_model(Track)

GroupModel = create_pydantic_model(Group, include_default_columns=True)
class GroupOut(GroupModel):
    players: list[PlayerOut]
    tracks: list[TrackModel]
