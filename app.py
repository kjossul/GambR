from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from piccolo.engine import engine_finder
from piccolo_admin.endpoints import create_admin

from api.endpoints import app as api
from api.piccolo_app import APP_CONFIG
from api.scheduler import scheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
        conf = engine.config
        conn_url = f"postgresql://{conf['user']}:{conf['password']}@{conf['host']}:{conf['port']}/{conf['database']}"
        jobstores = {"default": SQLAlchemyJobStore(url=conn_url)}
        scheduler.configure(jobstores=jobstores)
        scheduler.start()
    except Exception as e:
        print(e)
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
        scheduler.shutdown()
    except Exception:
        print("Unable to connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_database_connection_pool()
    yield
    await close_database_connection_pool()


app = FastAPI(lifespan=lifespan)
app.mount("/api", api)
# todo remove from production maybe
app.mount("/admin", create_admin(
    tables=APP_CONFIG.table_classes,
    # Required when running under HTTPS:
    # allowed_hosts=['my_site.com']    
))
