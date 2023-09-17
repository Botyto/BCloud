import logging
from typing import List, Dict, Callable

logger = logging.getLogger(__name__)


class Messages:
    handlers: Dict[str, List[Callable]]

    def __init__(self):
        self.handlers = {}

    def register(self, msg: str, fn: Callable):
        msg_handlers = self.handlers.get(msg)
        if msg_handlers is None:
            msg_handlers = []
            self.handlers[msg] = msg_handlers
        msg_handlers.append(fn)
        return fn

    def emit(self, msg: str, *args, **kwargs):
        msg_handlers = self.handlers.get(msg, None)
        if msg_handlers is None:
            return
        for handler in msg_handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error("Error while handling msg `%s`", msg)
                logger.exception(e)
