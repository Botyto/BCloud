from core.miniapp.miniapp import Miniapp, SqlEventRegistry, ModuleRegistry

from .tools.repetition import UpdateEventFromToCaches
from .calendars import CalendarModule


class ScheduleMiniapp(Miniapp):
    def __init__(self):
        super().__init__("schedule",
            SqlEventRegistry(UpdateEventFromToCaches),
            ModuleRegistry(CalendarModule),
        )
