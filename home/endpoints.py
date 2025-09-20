from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from tables import *
from schemas import *
import requests
import secrets

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# searchpath=os.path.join(os.path.dirname(__file__), "templates")

@app.get('/', response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("home.html.jinja", {
        "request": request,
        "title": "Piccolo + ASGI"
    })

@app.post('/auth')
async def post(auth: Auth):
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
    # generate secret and update player table
    token = secrets.token_hex(32)
    q = Player.insert(
        Player(uuid=user["account_id"], name=user["display_name"], secret=token)
    ).on_conflict(
        action="DO UPDATE",
        values=[Player.name, Player.secret]
    )
    q.run_sync()
    return Auth(token=token)
