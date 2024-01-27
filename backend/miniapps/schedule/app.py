from core.miniapp.miniapp import Miniapp, SqlEventRegistry

from .tools.repetition import UpdateEventFromToCaches


class ScheduleMiniapp(Miniapp):
    def __init__(self):
        super().__init__("schedule",
            SqlEventRegistry(UpdateEventFromToCaches),
        )
