import logging

from .context import AppContext

from ..http.context import ServerContext
from ..http.server import Server

logger = logging.getLogger(__name__)

class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        server_context = ServerContext(self.context)
        server = Server(server_context)
        server.run()
