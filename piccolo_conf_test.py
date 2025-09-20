from piccolo_conf import *  # noqa


DB = PostgresEngine(
    config={
        "database": "gambr_test",
        "user": DB_USER,
        "password": DB_PWD,
        "host": "localhost",
        "port": 5432,
    }
)
