from graphene import Schema
from typing import cast

from ..app.main import AppContext


class ServerContext(AppContext):
    graphene_schema: Schema

    def __init__(self, base: AppContext, graphene_scema: Schema):
        self._extend(base)
        self.graphene_schema = graphene_scema

    @property
    def port(self):
        return cast(int, self.env.get("PORT", 8080))

    @property
    def graphql_schema(self):
        return self.graphene_schema.graphql_schema
