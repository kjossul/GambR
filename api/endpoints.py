from typing import Annotated
from fastapi import FastAPI, Header, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .tables import *
from .models import *
import requests
import secrets
import asyncio
from uuid import UUID

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.post('/auth')
@limiter.limit("1/minute")
async def auth(request: Request, auth: Auth):
    # send authentication from plugin to openplanet to verify client
    op_url = "https://openplanet.dev/api/auth/validate"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "token": auth.token,
        "secret": None
    }
    r = requests.post(op_url, data=data, headers=headers)
    user = r.json()
    if "error" in user:
        raise HTTPException(status_code=400, detail="Invalid authentication")
    # generate unique secret and update player table
    # TODO move to jwt
    token = secrets.token_hex(32)
    while await Player.exists().where(Player.secret == token):
        token = secrets.token_hex(32)
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

@app.post('/clubs')
async def post_club(secret: Annotated[str, Header()], club: ClubModel):
    """
    Create a club
    """
    if not club.name or len(club.name) < 3:
        raise HTTPException(status_code=400, detail="Club name must be at least 3 characters long")
    if await Club.exists().where(Club.name == club.name):
        raise HTTPException(status_code=409, detail="Club name already exists")
    creator = await verify_secret(secret)
    g = Club(club.model_dump(exclude_none=True))
    await creator.add_m2m(
        g,
        m2m=Player.clubs,
        extra_column_values={"admin": True}
    )
    g = await Club.objects().get(Club.name == club.name)
    return JSONResponse({"id": g.id})

async def get_player_and_club(secret, club_name):
    club, player = await asyncio.gather(
        Club.objects().get(Club.name == club_name).run(),
        verify_secret(secret)
    )
    if not club:
        raise HTTPException(404, f"Club with name {club_name} does not exist.")
    return club, player

@app.put('/clubs/players')
async def join_club(secret: Annotated[str, Header()], name: str) -> ClubOut:
    """
    Join club
    """
    club, player = await get_player_and_club(secret, name)
    await club.add_m2m(
        player,
        m2m=Club.players
    )
    out = club.to_dict()
    members = await PlayerToClub.objects(PlayerToClub.player).where(PlayerToClub.club.id == club.id)
    tracks = await club.get_m2m(Club.tracks)
    out["players"] = [PlayerOut(points=p.points, admin=p.admin, **p.player.to_dict()) for p in members]
    out["tracks"] = [TrackModel(**t.to_dict()) for t in tracks]
    return ClubOut(**out)

@app.delete('/clubs/players')
async def leave_club(secret: Annotated[str, Header()], name: str):
    """
    leave club
    """
    club, player = await get_player_and_club(secret, name)
    await club.remove_m2m(
        player,
        m2m=Club.players
    )
    return JSONResponse("Club left successfully")

async def validate_membership(secret, club_id, requires_admin=False):
    club, members, player = await asyncio.gather(
        Club.objects().get(Club.id == club_id).run(),
        PlayerToClub.objects(PlayerToClub.player).where(PlayerToClub.club.id == club_id).run(),
        verify_secret(secret)
    )
    if not club:
        raise HTTPException(404, "Club does not exist.")
    try:
        m = next(m for m in members if m.player.id == player.id)
        if requires_admin and not m.admin:
            raise HTTPException(403, "You must be club admin to perform this action.")
    except StopIteration:
        raise HTTPException(403, "You are not part of this club.")
    return club, members

@app.get('/clubs/{club_id}')
async def get_club(secret: Annotated[str, Header()], club_id: int) -> ClubOut:
    """
    Get club info
    """
    club, members = await validate_membership(secret, club_id)
    tracks = await club.get_m2m(Club.tracks)
    out = club.to_dict()
    out["players"] = [PlayerOut(points=p.points, admin=p.admin, **p.player.to_dict()) for p in members]
    out["tracks"] = [TrackModel(**t.to_dict()) for t in tracks]
    return ClubOut(**out)

@app.post('/clubs/{club_id}')
async def update_club(secret: Annotated[str, Header()], club_id: int, club: ClubUpdate):
    """
    Update club settings
    """
    g, _ = await validate_membership(secret, club_id, requires_admin=True)
    for k,v in club.model_dump(exclude_none=True).items():
        setattr(g, k, v)
    await g.save()
    return JSONResponse("Values updated successfully")

@app.delete('/clubs/{club_id}')
async def delete_club(secret: Annotated[str, Header()], club_id: int):
    """
    Delete club
    """
    g, _ = await validate_membership(secret, club_id, requires_admin=True)
    await g.remove()
    return JSONResponse("Club deleted successfully.")

@app.put('/clubs/{club_id}/tracks')
async def add_club_tracks(secret: Annotated[str, Header()], club_id: int, tracks: list[TrackModel]):
    """
    add track(s) to a club
    """
    g, _ = await validate_membership(secret, club_id, requires_admin=True)
    ts = await asyncio.gather(*[Track.objects().get_or_create(
        Track.uuid == t.uuid, defaults={Track.name: t.name}
    ).run() for t in tracks])
    await asyncio.gather(*[g.add_m2m(t, m2m=Club.tracks).run() for t in ts])
    return JSONResponse("Tracks added successfully")

@app.delete('/clubs/{club_id}/tracks')
async def remove_club_tracks(secret: Annotated[str, Header()], club_id: int, uuids: Annotated[list[UUID], Query()]):
    """
    remove track(s) from a club
    """
    g, _ = await validate_membership(secret, club_id, requires_admin=True)
    ts = await Track.objects().where(
        Track.uuid.is_in(uuids)
    )
    await g.remove_m2m(
        *ts,
        m2m=Club.tracks
    )
    return JSONResponse("Tracks removed successfully")
