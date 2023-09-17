from asyncio import AbstractEventLoop, get_event_loop, sleep
from datetime import datetime
import logging
import time
from typing import Any, Callable, Dict

from .schedule import Schedule

logger = logging.getLogger(__name__)


CronjobCallable = Callable[[], Any]


class Scheduler:
    loop: AbstractEventLoop
    schedules: Dict[CronjobCallable, Schedule]

    def __init__(self, loop: AbstractEventLoop|None = None):
        self.schedules = {}
        self.loop = loop or get_event_loop()

    def run(self):
        self.loop.create_task(self.__loop())

    def schedule(self, fn: CronjobCallable, schedule: Schedule):
        assert fn not in self.schedules, f"Function `{fn}` already scheduled"
        self.schedules[fn] = schedule

    async def __loop(self):
        now = datetime.now()
        last_minute = now.minute
        while True:
            now = datetime.now()
            next_minute = datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=now.hour,
                minute=(now.minute + 1) % 60,
                second=0)
            await sleep((next_minute - now).total_seconds())

            # Ensure we don't trigger on the same minute twice
            now = datetime.now()
            if now.minute == last_minute:
                continue
            last_minute = now.minute

            for fn, schedule in self.schedules.items():
                if schedule.match(now):
                    start = time.time()
                    try:
                        fn()
                    except Exception as e:
                        logger.error(f"Error while running scheduled job `{fn}`")
                        logger.exception(e)
                    elapsed = time.time() - start
                    if elapsed > 1:
                        logger.warning(f"Job `{fn}` took {elapsed} seconds to run")
