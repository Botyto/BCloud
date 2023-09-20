from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.data import User
from core.auth.manager import UserManager
from core.graphql.context import GraphQLContext


class RegisterResult:
    pass


class LoginResult:
    pass


class LogoutResult:
    pass


class AuthModule(GqlMiniappModule):
    manager: UserManager

    def __init__(self, root, context: GraphQLContext):
        super().__init__(root, context)
        self.manager = UserManager(self.context, self.session)

    @query()
    def get_user(self) -> User:
        pass

    @mutation()
    def register(self, username: str, password: str) -> RegisterResult:
        user = self.manager.register(username, password)
        login, data = self.manager.login(username, password, self.request)
        self.authenticate(data)

    @mutation()
    def login(self, username: str, password: str) -> LoginResult:
        login, data = self.manager.login(username, password, self.request)
        self.authenticate(data)

    @mutation()
    def logout(self) -> LogoutResult:
        self.manager.logout(self.login_id)
