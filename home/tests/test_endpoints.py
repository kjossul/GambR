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
        await ModelBuilder.build(Player, defaults={"id": 1, "name": "1", "secret": "secret"})

    async def asyncTearDown(self):
        await drop_db_tables(*TABLES)

    async def test_group(self):
        # test group creation
        headers = {"secret": "secret"}
        data = {
            "name": "test"        
        }
        response = client.post("/groups", headers=headers, json=data)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert await Group.count() == 1
        assert await PlayerToGroup.count() == 1
        # test group endpoints
        response = client.get("/groups/1", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        new_settings = {
            "points_name": "shutupi",
            "automated_end": "PT1H"
        }
        response = client.post("/groups/1", headers=headers, json=new_settings)
        assert await Group.exists().where(Group.points_name == "shutupi")
        await ModelBuilder.build(Player, defaults={"id": 2, "name": "2", "secret": "foo"})
        response = client.get("/groups/1", headers={"secret": "foo"})
        assert response.status_code == 403
        # test group join
        response = client.put("/groups/players", headers={"secret": "foo"}, params=data)
        for member in response.json()["players"]:
            if member["name"] == "1":
                assert member["admin"]
            else:
                assert not member["admin"]
        response = client.delete("/groups/players", headers={"secret": "foo"}, params=data)
        assert await PlayerToGroup.count() == 1