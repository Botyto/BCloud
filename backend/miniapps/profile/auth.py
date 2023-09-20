from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.manager import UserManager


class AuthModule(GqlMiniappModule):
    manager: UserManager

    def __init__(self):
        self.manager = UserManager(self.context, self.session)

    @query()
    def get_user(self):
        pass

    @mutation()
    def register(self, username: str, password: str):
        user = self.manager.register(username, password)
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)

    @mutation()
    def login(self, username: str, password: str):
        login, data = self.manager.login(username, password, self.handler.request)
        self.handler.authenticate(data)

    @mutation()
    def logout(self):
        self.manager.logout(self.login_id)
