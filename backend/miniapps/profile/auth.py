from dataclasses import dataclass
from sqlalchemy import select

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.data import User, UserRole
from core.auth.handlers import AuthError
from core.auth.manager import UserManager
from core.graphql.result import SuccessResult


@dataclass
class LoginResult:
    jwt: str


class AuthModule(GqlMiniappModule):
    _manager: UserManager|None = None

    def __init__(self, handler, context):
        super().__init__(handler, context)

    @property
    def manager(self):
        if self._manager is None:
            self._manager = UserManager(self.context, self.session)
        return self._manager

    @query()
    def user(self) -> User|None:
        user_id = self.handler.current_user
        if user_id is None:
            return None
        statement = select(User).where(User.id == user_id)
        return self.session.scalars(statement).one_or_none()

    @mutation()
    def register(self, username: str, password: str) -> LoginResult:
        user = self.manager.register(username, password, UserRole.USER)
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)
        return LoginResult(jwt=self.handler.encode_jwt(data))

    @mutation()
    def login(self, username: str, password: str) -> LoginResult:
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)
        return LoginResult(jwt=self.handler.encode_jwt(data))

    @mutation()
    def logout(self) -> SuccessResult:
        if self.login_id is None:
            raise AuthError("Invalid login")
        self.manager.logout(self.login_id)
        return SuccessResult()
