from .modules.api import ApiMiniappModule, urlspec

from ..api.handlers import ApiHandlerMixin
from ..graphql.handlers import BaseGraphQLHandler, BaseGraphQLSubscriptionHandler, BaseSchemaHandler
from ..miniapp.miniapp import Miniapp, ModuleRegistry

def empty_func(_):
    pass


@urlspec(r"/api/graphql", None, "graphql")
class GraphQLModule(ApiMiniappModule, ApiHandlerMixin, BaseGraphQLHandler):
    @property
    def graphql_context(self):
        return self.api_context


@urlspec(r"/api/graphql/subscription", None, "graphql/subscription")
class GraphQLSubscriptionModule(ApiMiniappModule, ApiHandlerMixin, BaseGraphQLSubscriptionHandler):
    @property
    def graphql_context(self):
        return self.api_context

    def _get_login_jwt(self):
        if self.auth_token is not None:
            return self.auth_token
        return super()._get_login_jwt()


@urlspec(r"/api/graphql/schema", None, "graphql/schema")
class GraphQLSchemaModule(ApiMiniappModule, BaseSchemaHandler):
    pass


class GraphQLMiniapp(Miniapp):
    def __init__(self):
        super().__init__("gql",
            ModuleRegistry(GraphQLModule),
            ModuleRegistry(GraphQLSubscriptionModule),
            ModuleRegistry(GraphQLSchemaModule),
        )
