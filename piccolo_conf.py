from piccolo.engine.postgres import PostgresEngine
from configparser import RawConfigParser, UNNAMED_SECTION
from piccolo.conf.apps import AppRegistry
from platformdirs import user_data_dir
from pathlib import Path
import os

secrets = RawConfigParser(allow_unnamed_section=True)
secrets.read("secrets.ini")
NADEO_USER_AGENT = secrets.get(UNNAMED_SECTION, "user_agent")
NADEO_USER = secrets.get(UNNAMED_SECTION, "nadeo_user")
NADEO_PASSWORD = secrets.get(UNNAMED_SECTION, "nadeo_pwd")
DATA_DIR = user_data_dir("gambr", "kjossul")
Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
DB_USER = secrets.get(UNNAMED_SECTION, "psql_user")
DB_PWD = secrets.get(UNNAMED_SECTION, "psql_pwd")

DB = PostgresEngine(
    config={
        "database": "gambr",
        "user": DB_USER,
        "password": DB_PWD,
        "host": "localhost",
        "port": 5432,
    }
)

APP_REGISTRY = AppRegistry(
    apps=["api.piccolo_app", "piccolo_admin.piccolo_app"]
)
