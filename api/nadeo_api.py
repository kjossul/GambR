import time
import nadeo_api
import nadeo_api.auth
import nadeo_api.core
import nadeo_api.live
import nadeo_api.config
import pickle
from pathlib import Path 
from piccolo_conf import NADEO_PASSWORD, NADEO_USER, NADEO_USER_AGENT, DATA_DIR

nadeo_api.config.wait_between_requests_ms = 3000
nadeo_api.config.debug_logging = True

class NadeoAPI:
    def __init__(self):
        self.tokens = {}
        for audience in ("NadeoServices", "NadeoLiveServices"):
            try:
                filename = Path(DATA_DIR, audience).with_suffix(".pkl")
                with open(filename, 'rb') as f:
                    token = pickle.load(f)
                self.tokens[audience] = token
            except IOError:
                token = nadeo_api.auth.get_token(audience, NADEO_USER, NADEO_PASSWORD, NADEO_USER_AGENT, server_account=True)
                time.sleep(1)
                with open(filename, 'wb') as f:
                    pickle.dump(token, f)

    def get_records(self, player_uuids, map_uuid):
        endpoint = "/v2/mapRecords/"
        params = {
            "accountIdList": player_uuids,
            "mapId": map_uuid
        }
        return nadeo_api.core.get(self.tokens["NadeoServices"], endpoint, params)
