from piccolo.testing.test_case import AsyncTransactionTest
from fastapi.testclient import TestClient
from ..endpoints import app

client = TestClient(app)

class TestEndpoints(AsyncTransactionTest):
    async def test_group(self):
        pass