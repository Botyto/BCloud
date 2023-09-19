import base64

from .handlers import BaseGraphQLHandler, BaseGraphQLSubscriptionHandler, BaseSchemaHander


# (r"/graphql", None, "graphql")
class GraphQLHandler(ServiceHandlerMixin, BaseGraphQLHandler):
    @property
    def graphql_context(self):
        return self.api_context


# (r"/graphql/subscription", None, "graphql/subscription")
class GraphQLSubscriptionHandler(ServiceHandlerMixin, BaseGraphQLSubscriptionHandler):
    @property
    def graphql_context(self):
        return self.api_context

    def _extract_token(self):
        if self.auth_token:
            token = base64.b64decode(self.auth_token).decode("ascii")
            session_id, session_key = self._parse_str_token(token)
            return session_id, session_key
        return None, None


# (r"/graphql/schema", None, "graphql/schema")
class GraphQLSchemaHander(BaseSchemaHander):
    pass
