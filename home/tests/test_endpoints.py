from unittest import IsolatedAsyncioTestCase
from piccolo.testing.model_builder import ModelBuilder
from piccolo.table import create_db_tables, drop_db_tables
from piccolo.conf.apps import Finder
from fastapi.testclient import TestClient
from ..endpoints import app
from ..models import *

client = TestClient(app)
TABLES = Finder().get_table_classes()

class TestEndpoints(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await create_db_tables(*TABLES) 
        await ModelBuilder.build(Player, defaults={"secret": "secret"})

    async def asyncTearDown(self):
        await drop_db_tables(*TABLES)

    async def test_group(self):
        headers = {"secret": "secret"}
        data = {
            "name": "test"
        }
        response = client.post("/groups", headers=headers, json=data)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert await Group.count() == 1
        assert await PlayerToGroup.count() == 1