import os
from typing import Annotated
from fastapi import FastAPI, Request, Depends, Header, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .models import *
from .schemas import *
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
    }  # todo (validate data before sending also to avoid unnecessary calls)
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
    p = await Player.objects().get(Player.secret == secret)
    if not p:
        raise HTTPException(status_code=400, detail="secret invalid")
    return p

@app.post('/groups')
async def post_group(secret: Annotated[str, Header()], group: GroupModel):
    """
    Create a group
    """
    if not group.name or len(group.name) < 3:
        raise HTTPException(status_code=400, detail="Group name must be at least 3 characters long")
    if await Group.exists().where(Group.name == group.name):
        raise HTTPException(status_code=409, detail="Group name already exists")
    creator = await verify_secret(secret)
    g = Group(group.model_dump(exclude_none=True))
    await creator.add_m2m(
        g,
        m2m=Player.groups,
        extra_column_values={"admin": True}
    )
    g = await Group.objects().get(Group.name == group.name)
    return JSONResponse({"id": g.id})

@app.put('/groups/players')
async def join_group(secret: Annotated[str, Header()], name: str) -> GroupOut:
    """
    Join group
    """
    group = await Group.objects().get(Group.name == name)
    if not group:
        raise HTTPException(404, f"Group with name {name} does not exist.")
    player = await verify_secret(secret)
    await group.add_m2m(
        player,
        m2m=Group.players
    )
    out = group.to_dict()
    members = await PlayerToGroup.objects(PlayerToGroup.player).where(PlayerToGroup.group.id == group.id)
    tracks = await group.get_m2m(Group.tracks)
    out["players"] = [PlayerOut(points=p.points, admin=p.admin, **p.player.to_dict()) for p in members]
    out["tracks"] = [TrackModel(**t.to_dict()) for t in tracks]
    return GroupOut(**out)

@app.delete('/groups/players')
async def leave_group(secret: Annotated[str, Header()], name: str):
    """
    leave group
    """
    group = await Group.objects().get(Group.name == name)
    if not group:
        raise HTTPException(404, f"Group with name {name} does not exist.")
    player = await verify_secret(secret)    
    await group.remove_m2m(
        player,
        m2m=Group.players
    )
    return JSONResponse("Group left successfully")

@app.get('/groups/{group_id}')
async def get_group(secret: Annotated[str, Header()], group_id: int) -> GroupOut:
    """
    Get group info
    """
    player = await verify_secret(secret)
    group = await Group.objects().get(Group.id == group_id)
    members = await PlayerToGroup.objects(PlayerToGroup.player).where(PlayerToGroup.group.id == group_id)
    if not any(p.player.id == player.id for p in members):
        raise HTTPException(403, detail="You are not part of this group.")
    tracks = await group.get_m2m(Group.tracks)
    out = group.to_dict()
    out["players"] = [PlayerOut(points=p.points, admin=p.admin, **p.player.to_dict()) for p in members]
    out["tracks"] = [TrackModel(**t.to_dict()) for t in tracks]
    return GroupOut(**out)

@app.post('/groups/{group_id}')
async def update_group(secret: Annotated[str, Header()], group_id: int, group: GroupUpdate):
    """
    Update group settings
    """
    player = await verify_secret(secret)
    g = await Group.objects().get(Group.id == group_id)
    p = await PlayerToGroup.objects().get(
        (PlayerToGroup.player == player.id) & (PlayerToGroup.group == group_id)
    )
    if not p.admin:
        raise HTTPException(403, "You must be admin to change group settings.")
    # todo validate some settings if needed
    for k,v in group.model_dump(exclude_none=True).items():
        setattr(g, k, v)
    await g.save()
    return JSONResponse("Values updated successfully")

@app.delete('/groups/{group_id}')
async def delete_group(secret: Annotated[str, Header()], group_id: int):
    """
    Delete group
    """
    player = await verify_secret(secret)
    g = await Group.objects().get(Group.id == group_id)
    p = await PlayerToGroup.objects().get(
        (PlayerToGroup.player == player.id) & (PlayerToGroup.group == group_id)
    )
    if not p.admin:
        raise HTTPException(403, "You must be admin to delete the group")
    await g.remove()
    return JSONResponse("Group deleted successfully.")