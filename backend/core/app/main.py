import logging

from .context import AppContext

from ..http.context import ServerContext
from ..http.server import Server

logger = logging.getLogger(__name__)

import core.auth.data


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        self.context.miniapps.start()
        self.context.asyncjobs.start()
        server_context = ServerContext(self.context)
        server = Server(server_context)
        server.run()
