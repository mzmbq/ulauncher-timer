import logging
import re
from datetime import datetime, timedelta

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.event import BaseEvent, ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from timer import TimerManager

logger = logging.getLogger(__name__)


def parse_duration(s: str) -> timedelta | None:
    """Parse duration from strings like '1h 20m 30s' or '20m30s' or '45s'"""
    pattern = r"((?P<hours>\d?)\s?h)?\s?((?P<minutes>\d+)\s?m)?\s?((?P<seconds>\d+)\s?s)?"
    match = re.match(pattern, s)
    if match is None:
        return
    logger.info(f"Matched groups: {match.groupdict()}")

    hs = int(match.group("hours") or 0)
    ms = int(match.group("minutes") or 0)
    ss = int(match.group("seconds") or 0)

    if hs > 99999 or ms > 99999 or ss > 99999:
        return None

    duration = timedelta(hours=hs, minutes=ms, seconds=ss)
    if duration == timedelta(0):
        return None

    return duration


def parse_message(s: str) -> str:
    """Parse everything after the first ':' as message"""
    msg = s.split(":")
    if len(msg) < 2:
        return ""
    return ":".join(msg[1:]).strip()


class TimerExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())

        self.timer_manager = TimerManager(
            notification_type=self.preferences.get(
                "notification_type", "no-send"),
            notification_url=self.preferences.get("notification_url", ""),
        )

    def active_timers(self) -> list[ExtensionResultItem]:
        timers = []
        for timer in self.timer_manager.get_active_timers():
            data = {"action": "cancel",
                    "timer_id": timer.id}
            remaining = str(
                timer.scheduled_time - datetime.now()).split(".")[0]
            message = timer.message or f"Timer \"{timer.id[:4]}\""
            timers.append(ExtensionResultItem(
                icon="images/icon.png",
                name=f"{message}. Remaining: {remaining}/{timer.duration}",
                on_enter=ExtensionCustomAction(data, keep_app_open=True),
            ))

        return timers


class KeywordQueryEventListener(EventListener):

    def on_event(self, event: BaseEvent, extension: Extension) -> list[ExtensionResultItem]:
        if not isinstance(event, KeywordQueryEvent):
            logger.error("Event it not of type KeywordQueryEvent")
            return []
        if not isinstance(extension, TimerExtension):
            logger.error("Extension is not of type TimerExtension")
            return []
        return self._on_event(event, extension)

    def _on_event(self, event: KeywordQueryEvent, extension: TimerExtension) -> list[ExtensionResultItem]:
        user_input = event.get_argument()

        if user_input is None or user_input.strip() == "":
            logger.info("No user input, showing active timers")
            return extension.active_timers()

        duration = parse_duration(user_input)
        if duration is None:
            return []

        data = {"action": "set",
                "timer_duration": duration,
                "message": parse_message(user_input),
                }
        return [ExtensionResultItem(icon="images/icon.png",
                                    name=f"Set timer for {duration}",
                                    on_enter=ExtensionCustomAction(
                                        data, keep_app_open=False),
                                    )]


class ItemEnterEventListener(EventListener):

    def on_event(self, event: BaseEvent, extension: Extension) -> list[ExtensionResultItem]:
        if not isinstance(event, ItemEnterEvent):
            logger.error("Event it not of type ItemEnterEvent")
            return []
        if not isinstance(extension, TimerExtension):
            logger.error("Extension is not of type TimerExtension")
            return []
        return self._on_event(event, extension)

    def _on_event(self, event: ItemEnterEvent, extension: TimerExtension) -> list[ExtensionResultItem]:
        data = event.get_data()

        match data.get("action"):
            case "cancel":
                timer_id = data.get("timer_id")
                extension.timer_manager.cancel_timer(timer_id)
                logger.info(f"Cancelled timer with id {timer_id}")
                return extension.active_timers()
            case "set":
                timer_duration = data.get("timer_duration")
                extension.timer_manager.add_timer(
                    timer_duration, message=data.get("message"))
                logger.info(f"Set timer for duration {timer_duration}")

        return []


if __name__ == '__main__':
    TimerExtension().run()
