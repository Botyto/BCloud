import logging
import tornado.ioloop
import tornado.web

from .context import ServerContext

logger = logging.getLogger(__name__)


class Server:
    context: ServerContext
    app: tornado.web.Application

    def __init__(self, context: ServerContext):
        self.context = context

    def run(self):
        port = self.context.port
        self.app = tornado.web.Application()
        logger.info("Listening on port %d", port)
        self.app.listen(port)
        tornado.ioloop.IOLoop.current().start()
