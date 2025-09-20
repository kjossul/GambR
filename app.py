from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin

from home.endpoints import app as home_app
from home.piccolo_app import APP_CONFIG


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_database_connection_pool()
    yield
    await close_database_connection_pool()


app = FastAPI()
app.mount("/", home_app)
app.mount("/admin", create_admin(
    tables=APP_CONFIG.table_classes,
    # Required when running under HTTPS:
    # allowed_hosts=['my_site.com']    
))
app.mount("/static", StaticFiles(directory="static"), name="static")
