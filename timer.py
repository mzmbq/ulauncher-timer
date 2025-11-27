import logging
import uuid

from datetime import datetime, timedelta
from dataclasses import dataclass
import threading
import subprocess as s


logger = logging.getLogger(__name__)


@dataclass
class Timer:
    id: str
    scheduled_time: datetime
    duration: timedelta
    t_timer: threading.Timer
    message: str = ""


class TimerManager:
    def __init__(self, send_notification: bool = True, token: str = ""):
        self.lock = threading.Lock()
        self.timers: dict[str, Timer] = {}

        # Config
        self.send_notification = send_notification
        self.token = token

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

        if self.send_notification:
            s.call(["notify-send", "Time's Up", msg])
        if self.token:
            # TODO: implement
            pass

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
