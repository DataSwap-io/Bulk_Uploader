# schedule_utils.py
from datetime import datetime, timedelta
import itertools

EU_TZ = "Europe/Amsterdam"

SCHEDULE = {
    "Instagram Reels": {0:["10:00","19:00"], 2:["11:00","20:00"], 4:["09:00","18:00"]},
    "TikTok":          {1:["16:00","19:00"], 3:["09:00","14:00"], 4:["16:00","17:00"]},
    "YouTube Shorts":  {4:["17:00","20:00"], 5:["15:00","18:00"], 6:["12:00","17:00"]},
}

def next_slots(start_date, tz=EU_TZ):
    order = ["Instagram Reels", "TikTok", "YouTube Shorts"]
    day = start_date.date()
    while True:
        for platform in order:
            dow = day.weekday()
            if dow in SCHEDULE[platform]:
                for t in SCHEDULE[platform][dow]:
                    hour, minute = map(int, t.split(":"))
                    slot = datetime.combine(day, datetime.min.time()) \
                        + timedelta(hours=hour, minutes=minute)
                    if slot > start_date:
                        yield platform, slot
        day += timedelta(days=1)
