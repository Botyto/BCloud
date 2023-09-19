import base64

from .handlers import BaseGraphQLHandler, BaseGraphQLSubscriptionHandler, BaseSchemaHander

from ..api.handlers import ApiHandlerMixin


# (r"/graphql", None, "graphql")
class GraphQLHandler(ApiHandlerMixin, BaseGraphQLHandler):
    @property
    def graphql_context(self):
        return self.api_context


# (r"/graphql/subscription", None, "graphql/subscription")
class GraphQLSubscriptionHandler(ApiHandlerMixin, BaseGraphQLSubscriptionHandler):
    @property
    def graphql_context(self):
        return self.api_context

    def _get_login_jwt(self):
        if self.auth_token is not None:
            return self.auth_token
        return super()._get_login_jwt()


# (r"/graphql/schema", None, "graphql/schema")
class GraphQLSchemaHander(BaseSchemaHander):
    pass
