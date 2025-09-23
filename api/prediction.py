from apscheduler.schedulers.background import BlockingScheduler
from .tables import *
from datetime import datetime
from enum import IntEnum
import asyncio
from .nadeo_api import NadeoAPI

class PredictionType(IntEnum):
    VERSUS = 0
    GUESS = 1
    RAFFLE = 2

class PredictionManager:
    def __init__(self):
        self.nadeo_api = NadeoAPI()
        self.scheduler = BlockingScheduler()
        # todo add nadeo api token initialization

    def start(self, interval_minutes=1):
        self.scheduler.add_job(self.process_expired_predictions, trigger='interval', minutes=interval_minutes)
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    async def process_expired_predictions(self):
        now = datetime.now()
        queue = await Prediction.objects(Prediction.track.uuid).where(
            (Prediction.ends_at < now()) & (not Prediction.processed)
        )
        for prediction in queue:
            records = await prediction.get_records()
            if prediction.type == PredictionType.VERSUS:
                pass
            elif prediction.type == PredictionType.GUESS:
                pass
            elif prediction.type == PredictionType.RAFFLE:
                pass # todo not implemented

    def update_records(self, prediction):
        pass
        

monitor = PredictionManager()