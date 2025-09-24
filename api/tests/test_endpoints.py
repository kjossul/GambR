from unittest import IsolatedAsyncioTestCase
import asyncio
from piccolo.testing.model_builder import ModelBuilder
from piccolo.table import create_db_tables, drop_db_tables
from piccolo.conf.apps import Finder
from fastapi.testclient import TestClient
from ..endpoints import app
from ..tables import *

client = TestClient(app)
TABLES = Finder().get_table_classes()

class TestEndpoints(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await create_db_tables(*TABLES),

    async def asyncTearDown(self):
        await drop_db_tables(*TABLES)

    async def test_club(self):
        await asyncio.gather(
            ModelBuilder.build(Player, defaults={"id": 1, "name": "1", "secret": "1"}),
            ModelBuilder.build(Player, defaults={"id": 2, "name": "2", "secret": "2"})
        )
        # test club creation
        headers1 = {"secret": "1"}
        headers2 = {"secret": "2"}
        data = {"name": "test"}
        response = client.post("/clubs", headers=headers1, json=data)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        assert await PlayerToClub.count() == 1
        # test club endpoints
        response = client.get("/clubs/1", headers=headers1)
        assert response.status_code == 200
        assert response.json()["id"] == 1
        new_settings = {
            "points_name": "shutupi",
            "automated_end": "PT1H"
        }
        response = client.post("/clubs/1", headers=headers1, json=new_settings)
        assert await Club.exists().where(Club.points_name == "shutupi")
        response = client.get("/clubs/1", headers=headers2)
        assert response.status_code == 403
        # test club join and leave
        response = client.put("/clubs/players", headers=headers2, params=data)
        for member in response.json()["players"]:
            if member["name"] == "1":
                assert member["admin"]
            else:
                assert not member["admin"]
            assert member["points"] == 1000
        response = client.delete("/clubs/players", headers=headers2, params=data)
        assert await PlayerToClub.count() == 1
        # test tracks addition and deletion
        data = [
            {
                'uuid': "13f7c37b-6565-4091-81b7-bd5d834bd72f",
                'name': "Pokétech #001"
            },
            {
                'uuid': "70d16588-ca20-48de-a577-5729cf314cf7",
                'name': "Pokétech #002"                
            },
            {
                'uuid': "f7fc9239-0d4a-45ff-9186-e51ed23c6f9c",
                'name': "Pokétech #003"   
            }]
        # test for idempotency
        for _ in range(2):
            response = client.put("/clubs/1/tracks", headers=headers1, json=data)
            assert await Track.count() == 3
        response = client.delete("/clubs/1/tracks", headers=headers1, params={"uuids": [data[2]["uuid"]]})
        assert await asyncio.gather(
            Track.count(),
            TrackToClub.count()
        ) == [3, 2]
        response = client.delete("/clubs/1", headers=headers1)
        assert await Club.count() == 0

    async def test_prediction(self):
        pass