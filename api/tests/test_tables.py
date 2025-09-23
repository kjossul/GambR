from piccolo.testing.test_case import IsolatedAsyncioTestCase
from piccolo.testing.model_builder import ModelBuilder
from piccolo.conf.apps import Finder
from piccolo.table import create_db_tables, drop_db_tables

import asyncio
from datetime import datetime
from ..tables import *

TABLES = Finder().get_table_classes()
timestamps = [datetime.today().replace(hour=i) for i in range(5)]


class TestEndpoints(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await drop_db_tables(*TABLES)
        await create_db_tables(*TABLES),
        await asyncio.gather(
            ModelBuilder.build(Player, defaults={"id": 1, "name": "1"}),
            ModelBuilder.build(Player, defaults={"id": 2, "name": "2"}),
            ModelBuilder.build(Track, defaults={"id": 1}),
        )
    
    async def asyncTearDown(self):
        await drop_db_tables(*TABLES)

    async def test_prediction(self):
        await Club.insert(
            Club(name="1")
        )
        await TrackmaniaRecord.insert(
            TrackmaniaRecord(player=1, track=1, created_at=timestamps[0]),
            TrackmaniaRecord(player=1, track=1, created_at=timestamps[4]),
            TrackmaniaRecord(player=2, track=1, created_at=timestamps[2]),
            TrackmaniaRecord(player=2, track=1, created_at=timestamps[4]),
        )
        await Prediction.insert(
            Prediction(track=1, ends_at=timestamps[3])
        )
        prediction = await Prediction.objects(Prediction.track).get(Prediction.id == 1)
        players = await Player.objects()
        await prediction.add_m2m(
            *[p for p in players],
            m2m=Prediction.protagonists
        )
        records = await prediction.get_records()
        assert [tr["id"] for tr in records] == [2, 4]