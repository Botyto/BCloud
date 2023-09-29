from sqlalchemy import select

from core.api.pages import PagesInput, PagesResult
from core.api.modules.gql import GqlMiniappModule, query
from core.auth.data import Activity


class ActivityModule(GqlMiniappModule):
    @query()
    def log(self, pages: PagesInput) -> PagesResult[Activity]:
        if self.handler.current_user is None:
            return PagesResult.empty()
        statement = select(Activity).where(Activity.owner_id == self.handler.current_user)
        return pages.of(self.session, statement)
