from pydantic import BaseModel
from models import Player

class Auth(BaseModel):
    token: str

class RequestBase(BaseModel):
    secret: str

    async def get_player(self):
        return Player.select().where(Player.secret == self.secret)