import os
from typing import Annotated
from fastapi import FastAPI, Request, Depends, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from models import *
from schemas import *
import requests
import secrets

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get('/', response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("home.html.jinja", {
        "request": request,
        "title": "Piccolo + ASGI"
    })

@app.post('/auth')
async def auth(auth: Auth):
    # send authentication from plugin to openplanet to verify client
    op_url = "https://openplanet.dev/api/auth/validate"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "token": auth.token,
        "secret": None
    }  # todo (validate data before sending also to avoid unneccessary calls)
    r = requests.post(op_url, data=data, headers=headers)
    user = r.json()
    if "error" in user:
        raise HTTPException(status_code=400, detail="Invalid authentication")
    # generate unique secret and update player table
    token = secrets.token_hex(64)
    while await Player.exists().where(Player.secret == token):
        token = secrets.token_hex(64)
    await Player.insert(
        Player(uuid=user["account_id"], name=user["display_name"], secret=token)
    ).on_conflict(
        action="DO UPDATE",
        values=[Player.name, Player.secret]
    )
    return Auth(token=token)

async def verify_secret(secret: Annotated[str, Header()]):
    p = await Player.select().where(Player.secret == secret)
    if not p:
        raise HTTPException(status_code=400, detail="secret invalid")

@app.post('/groups', dependencies=[Depends(verify_secret)])
async def post_group(group: GroupModel):
    if await Group.exists().where(Group.name == group.name):
        raise HTTPException(status_code=409, detail="Group name already exists")
    # todo make user who created this admin
    id = await Group.insert(Group(group.model_dump(exclude_none=True))).returning(Group.id)
    return JSONResponse({"id": id})