from graphql import GraphQLResolveInfo

from ..auth.context import AuthContext


class GraphQLContext(AuthContext):
    info: GraphQLResolveInfo

    def __init__(self, base: AuthContext, info: GraphQLResolveInfo):
        self._extend(base)
        self.info = info
