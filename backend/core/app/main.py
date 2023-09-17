import logging

from .context import AppContext

from ..asyncjob.engine import AsyncJobs
from ..http.context import ServerContext
from ..http.server import Server
from ..miniapp.engine import Manager as MiniappsManager

logger = logging.getLogger(__name__)

import core.identity.data


class App:
    context: AppContext
    miniapps: MiniappsManager
    asyncjobs: AsyncJobs

    def __init__(self, context: AppContext):
        self.context = context
        self.miniapps = MiniappsManager(context)
        self.asyncjobs = AsyncJobs(context)

    def run(self):
        self.miniapps.start()
        self.asyncjobs.start()
        server_context = ServerContext(self.context)
        server = Server(server_context)
        server.run()
