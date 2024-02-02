from uuid import UUID
from typing import List

from sqlalchemy import select

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.api.pages import PagesInput, PagesResult
from core.auth.handlers import AuthError
from core.graphql.result import SuccessResult

from .data import ScheduleCalendar
from .tools.calendars import CalendarManager


class CalendarModule(GqlMiniappModule):
    _manager: CalendarManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = CalendarManager(self.user_id, self.session)
        return self._manager

    @query()
    def list(self) -> List[ScheduleCalendar]:
        statement = select(ScheduleCalendar) \
            .where(ScheduleCalendar.user_id == self.user_id)
        return list(self.session.scalars(statement).all())

    @mutation()
    def create(self, name: str) -> ScheduleCalendar:
        storage = self.manager.create(name)
        self.log_activity("calendar.create", {"id": str(storage.id), "name": name})
        return storage

    @mutation()
    def delete(self, id: UUID) -> SuccessResult:
        success, name = self.manager.delete(id)
        if success:
            self.log_activity("calendar.delete", {"id": str(id), "name": name})
        return SuccessResult(success)

    @mutation()
    def rename(self, id: UUID, name: str) -> ScheduleCalendar:
        previous, calendar = self.manager.rename(id, name)
        self.log_activity("calendar.rename", {"id": str(id), "new": name, "old": previous})
        return calendar
