from datetime import datetime
from zoneinfo import ZoneInfo

BUISINESS_TZ = ZoneInfo("Europe/Kyiv")

def get_buisiness_time_now() -> datetime:
    return datetime.now(BUISINESS_TZ)