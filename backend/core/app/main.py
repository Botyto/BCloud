import logging


from .context import AppContext

from ..graphql.schema.schema import SchemaBuilder
from ..http.context import ServerContext
from ..http.server import Server

logger = logging.getLogger(__name__)


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        self.context.asyncjobs.start()
        self.context.miniapps.start()
        schema_builder = SchemaBuilder(self.context.graphql_methods)
        graphene_schema = schema_builder.build()
        server_context = ServerContext(self.context, graphene_schema)
        server = Server(server_context)
        server.run()
