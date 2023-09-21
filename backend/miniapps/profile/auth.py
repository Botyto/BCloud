from dataclasses import dataclass

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.data import User
from core.auth.handlers import AuthError
from core.auth.manager import UserManager
from core.graphql.result import SuccessResult


@dataclass
class LoginResult:
    jwt: str


@dataclass
class RegisterResult(LoginResult):
    pass


class AuthModule(GqlMiniappModule):
    manager: UserManager

    def __init__(self, handler, context):
        super().__init__(handler, context)
        self.manager = UserManager(self.context, self.session)

    @query()
    def get_user(self) -> User|None:
        return None

    @mutation()
    def register(self, username: str, password: str) -> RegisterResult:
        user = self.manager.register(username, password)
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)

    @mutation()
    def login(self, username: str, password: str) -> LoginResult:
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)

    @mutation()
    def logout(self) -> SuccessResult:
        if self.login_id is None:
            raise AuthError("Invalid login")
        self.manager.logout(self.login_id)
        return SuccessResult()
