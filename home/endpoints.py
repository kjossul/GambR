import os

import jinja2
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException
from starlette.routing import Route
import requests
import json
import secrets
from tables import *


ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=os.path.join(os.path.dirname(__file__), "templates")
    )
)


class HomeEndpoint(HTTPEndpoint):
    async def get(self, request):
        template = ENVIRONMENT.get_template("home.html.jinja")

        content = template.render(
            title="Piccolo + ASGI",
        )

        return HTMLResponse(content)

class AuthEndpoint(HTTPEndpoint):
    async def post(self, request):
        # send authentication from plugin to openplanet to verify client
        op_url = "https://openplanet.dev/api/auth/validate"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "token": request.json()["token"],
            "secret": None
        }  # todo (validate data before sending also)
        r = requests.post(op_url, data=data, headers=headers)
        user = r.json()
        if "error" in user:
            raise HTTPException(status_code=400, detail="Invalid authentication")
        # generate secret and update player table
        secret = secrets.token_hex(32)
        q = Player.insert(
            Player(uuid=user["account_id"], name=user["display_name"], secret=secret)
        ).on_conflict(
            action="DO UPDATE",
            values=[Player.name, Player.secret]
        )
        q.run_sync()
        return JSONResponse({"secret": secret})
    
routes = [Route('/auth', AuthEndpoint)]