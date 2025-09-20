from piccolo.testing.test_case import AsyncTransactionTest
from piccolo.testing.model_builder import ModelBuilder
from fastapi.testclient import TestClient
from ..endpoints import app
from ..models import *

client = TestClient(app)

class TestEndpoints(AsyncTransactionTest):
    async def create_user(self):
        await ModelBuilder.build(Player, defaults={"secret": "secret"})

    async def test_group(self):
        pass