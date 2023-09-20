
from .modules.api import ApiMiniappModule, urlspec

from ..api.handlers import ApiHandlerMixin
from ..graphql.handlers import BaseGraphQLHandler, BaseGraphQLSubscriptionHandler, BaseSchemaHander
from ..miniapp.miniapp import Miniapp


@urlspec(r"/graphql", None, "graphql")
class GraphQLHandler(ApiHandlerMixin, ApiMiniappModule, BaseGraphQLHandler):
    @property
    def graphql_context(self):
        return self.api_context


@urlspec(r"/graphql/subscription", None, "graphql/subscription")
class GraphQLSubscriptionHandler(ApiHandlerMixin, ApiMiniappModule, BaseGraphQLSubscriptionHandler):
    @property
    def graphql_context(self):
        return self.api_context

    def _get_login_jwt(self):
        if self.auth_token is not None:
            return self.auth_token
        return super()._get_login_jwt()


@urlspec(r"/graphql/schema", None, "graphql/schema")
class GraphQLSchemaHander(ApiMiniappModule, BaseSchemaHander):
    pass

def empty_func(_):
    pass


class GraphQLMiniapp(Miniapp):
    def __init__(self):
        super().__init__("gql", empty_func, empty_func, [
            GraphQLHandler(self),
            GraphQLSubscriptionHandler(self),
            GraphQLSchemaHander(self),
        ], {}, True, None)
