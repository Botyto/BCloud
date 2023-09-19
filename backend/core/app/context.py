from ..graphql.schema.schema import SchemaBuilder
from ..miniapp.context import MiniappContext
from ..miniapp.engine import Manager as MiniappsManager


class AppContext(MiniappContext):
    miniapps: MiniappsManager
    graphql_schema_builder: SchemaBuilder

    def __init__(self,
        base: MiniappContext,
        miniapps: MiniappsManager,
    ):
        self._extend(base)
        self.miniapps = miniapps
        self.graphql_schema_builder = SchemaBuilder()
