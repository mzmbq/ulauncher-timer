import logging
import subprocess as s
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib import request
from urllib.parse import quote

logger = logging.getLogger(__name__)


@dataclass
class Timer:
    id: str
    scheduled_time: datetime
    duration: timedelta
    t_timer: threading.Timer
    message: str = ""


class TimerManager:
    def __init__(self, notification_type: str, notification_url: str):
        self.lock = threading.Lock()
        self.timers: dict[str, Timer] = {}

        # Config
        self.notification_type = notification_type
        self.notification_url = notification_url

    def on_finish(self, timer_id: str):
        timer = None
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
            del self.timers[timer_id]

        if not isinstance(timer, Timer):
            logger.error(f"Timer with id {timer_id} not found.")
            return

        msg = timer.message or f"Timer \"{timer_id[:4]}\" has finished."

        if self.notification_type != "off":
            s.call(["notify-send", "Time's Up", msg])
            if self.notification_type == "sound":
                # TODO: implement sound notification
                pass

        if self.notification_url:
            req_url = self.notification_url.replace(
                "{message}", quote(msg))
            logger.info(f"Sending request to {req_url}")
            request.urlopen(req_url)

    def add_timer(self, duration: timedelta, message: str):
        scheduled_time = datetime.now() + duration
        timer_id = uuid.uuid4().hex

        t_timer = threading.Timer(
            duration.total_seconds(),
            self.on_finish,
            args=(timer_id,),
        )
        timer = Timer(id=timer_id,
                      scheduled_time=scheduled_time,
                      duration=duration,
                      t_timer=t_timer,
                      message=message,
                      )

        with self.lock:
            self.timers[timer.id] = timer

        t_timer.start()

    def get_active_timers(self) -> list[Timer]:
        with self.lock:
            return list(self.timers.values())

    def cancel_timer(self, timer_id: str):
        with self.lock:
            if timer_id in self.timers:
                timer = self.timers[timer_id]
                timer.t_timer.cancel()
                del self.timers[timer_id]
