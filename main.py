import logging
from datetime import timedelta
from math import log
import re
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, BaseEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction


logger = logging.getLogger(__name__)


def parse_time(s: str) -> timedelta | None:
    # TODO: improve or find a better approach
    pattern = r"((?P<hours>\d+)\s?h)?\s?((?P<minutes>\d+)\s?m)?\s?((?P<seconds>\d+)\s?s)?"
    match = re.match(pattern, s)
    if match is None:
        return

    logger.info(f"Matched groups: {match.groupdict()}")

    duration = timedelta()
    if match.group("hours"):
        duration += timedelta(hours=int(match.group("hours")))
    if match.group("minutes"):
        duration += timedelta(minutes=int(match.group("minutes")))
    if match.group("seconds"):
        duration += timedelta(seconds=int(match.group("seconds")))

    if duration == timedelta(0):
        return None

    return duration


class TimerExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event: BaseEvent, extension: Extension):
        if not isinstance(event, KeywordQueryEvent):
            logger.error("Event it not of type KeywordQueryEvent")
            return

        user_input = event.get_argument()
        if user_input is None:
            user_input = ""
            return []

        duration = parse_time(user_input)
        if duration is None:
            return []

        return [ExtensionResultItem(icon="images/icon.png",
                                    name=f"Set timer for {duration}",
                                    on_enter=HideWindowAction())]


if __name__ == '__main__':
    TimerExtension().run()
