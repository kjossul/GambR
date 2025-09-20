from piccolo.engine.postgres import PostgresEngine
from configparser import RawConfigParser, UNNAMED_SECTION
from piccolo.conf.apps import AppRegistry
import os

secrets = RawConfigParser(allow_unnamed_section=True)
secrets.read("secrets.ini")
os.environ["GAMBR_USER_AGENT"] = secrets.get(UNNAMED_SECTION, "user_agent")
os.environ["GAMBR_NADEO_USER"] = secrets.get(UNNAMED_SECTION, "nadeo_user")
os.environ["GAMBR_NADEO_PWD"] = secrets.get(UNNAMED_SECTION, "nadeo_pwd")
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
    apps=["home.piccolo_app", "piccolo_admin.piccolo_app"]
)
