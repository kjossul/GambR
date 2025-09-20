from piccolo.utils.pydantic import create_pydantic_model
from pydantic import BaseModel
from models import *

class Auth(BaseModel):
    token: str

GroupModel = create_pydantic_model(Group)
