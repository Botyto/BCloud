import logging

logger = logging.getLogger(__name__)

HANDLERS = {}

def register(msg, fn):
    msg_handlers = HANDLERS.get(msg)
    if msg_handlers is None:
        msg_handlers = []
        HANDLERS[msg] = msg_handlers
    msg_handlers.append(fn)
    return fn

def handler(msg):
    def decorator(fn):
        return register(msg, fn)
    return decorator

def emit(msg, *args, **kwargs):
    msg_handlers = HANDLERS.get(msg, None)
    if msg_handlers is None:
        return
    for handler in msg_handlers:
        try:
            handler(*args, **kwargs)
        except Exception as e:
            logger.exception("Error while handling msg %s: %s", msg, e)
