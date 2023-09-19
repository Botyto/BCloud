# (r"/graphql/sandbox", None, "graphql/sandbox")
class GraphQLSandboxHandler(graphql_handlers.ApolloSandboxHandler):
    pass


# (r"/graphql", None, "graphql")
class GraphQLHandler(ServiceHandlerMixin, graphql_handlers.BaseGraphQLHandler):
    @property
    def graphql_context(self):
        return self.service_context


# (r"/graphql/subscription", None, "graphql/subscription")
class GraphQLSubscriptionHandler(ServiceHandlerMixin, graphql_handlers.BaseGraphQLSubscriptionHandler):
    @property
    def graphql_context(self):
        return self.service_context

    def _extract_token(self):
        if self.auth_token:
            token = base64.b64decode(self.auth_token).decode("ascii")
            session_id, session_key = self._parse_str_token(token)
            return session_id, session_key
        return None, None

# (r"/graphql/schema", None, "graphql/schema")
class GraphQLSchemaHander(graphql_handlers.BaseSchemaHander):
    pass
