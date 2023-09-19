from graphql import GraphQLResolveInfo

from ..api.context import ApiContext


class GraphQLContext(ApiContext):
    info: GraphQLResolveInfo

    def __init__(self, base: ApiContext, info: GraphQLResolveInfo):
        self._extend(base)
        self.info = info
