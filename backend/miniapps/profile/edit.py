from sqlalchemy import select
from core.auth.data import User

from core.api.modules.gql import GqlMiniappModule, mutation
from core.graphql.result import SuccessResult


class EditModule(GqlMiniappModule):
    @property
    def user(self):
        user_id = self.user_id
        if user_id is None:
            return None
        statement = select(User).where(User.id == user_id)
        return self.session.scalars(statement).one_or_none()

    @mutation()
    def display_name(self, display_name: str) -> SuccessResult:
        if self.user is None:
            return SuccessResult(False)
        old_name = self.user.display_name
        self.user.display_name = display_name
        self.log_activity("edit.display_name", {"old": old_name, "new": display_name})
        return SuccessResult(True)
