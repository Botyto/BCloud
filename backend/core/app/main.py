import logging
import time

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
        self.context.miniapps.start()
        self.context.asyncjobs.start()
        schema_builder = SchemaBuilder(self.context.graphql_methods, "miniapps")
        graphene_schema = schema_builder.build()
        server_context = ServerContext(self.context, graphene_schema)
        server = Server(server_context)
        logger.info(f"App startup time: %.3fs", time.time() - self.context.app_init_time)
        logger.info(f"Total startup time: %.3fs", time.time() - self.context.init_time)
        server.run()
