from dataclasses import dataclass
from sqlalchemy import select
from typing import Tuple

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.data import User, UserRole, Login
from core.auth.handlers import AuthError
from core.auth.manager import UserManager
from core.graphql.result import SuccessResult


@dataclass
class LoginResult:
    jwt: str


class AuthModule(GqlMiniappModule):
    _manager: UserManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            self._manager = UserManager(self.context, self.session)
        return self._manager

    @query()
    def user(self) -> User|None:
        user_id = self.user_id
        if user_id is None:
            return None
        statement = select(User).where(User.id == user_id)
        return self.session.scalars(statement).one_or_none()

    @mutation()
    def register(self, username: str, password: str) -> LoginResult:
        user = self.manager.register(username, password, UserRole.USER)
        login, result = self.__internal_login(username, password)
        self.log_activity("auth.register")
        self.__log_login(login)
        return result

    def __internal_login(self, username: str, password: str) -> Tuple[Login, LoginResult]:
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)
        return login, LoginResult(jwt=self.handler.encode_jwt(data))

    def __log_login(self, login: Login):
        self.log_activity("auth.login", {"id": str(login.id)})

    @mutation()
    def login(self, username: str, password: str) -> LoginResult:
        login, result = self.__internal_login(username, password)
        self.__log_login(login)
        return result

    @mutation()
    def logout(self) -> SuccessResult:
        if self.login_id is None:
            raise AuthError("Invalid login")
        self.manager.logout(self.login_id)
        self.log_activity("auth.logout", {"id": str(self.login_id)})
        return SuccessResult()
