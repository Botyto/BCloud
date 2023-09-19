import logging
import tornado.ioloop
from tornado.platform.asyncio import AsyncIOMainLoop
from tornado.routing import URLSpec
from tornado.web import Application
from typing import cast

from .context import ServerContext

logger = logging.getLogger(__name__)


class Server:
    context: ServerContext
    loop: AsyncIOMainLoop
    app: Application

    def __init__(self, context: ServerContext):
        self.context = context
        self.app = Application(
            handlers=self._gather_handlers(),  # type: ignore
            template_path="templates",
            static_path="static",
            cookie_secret=self.env.get("COOKIE_SECRET", "PLACEHOLDER"),
            compiled_template_cache=True,
            static_hash_cache=True,
            compress_response=True,
            debug=self.env.debug,
            autoreload=False,
            server_context=self.context,
        )
        self.loop = cast(AsyncIOMainLoop, tornado.ioloop.IOLoop.current())
        if self.env.debug:
            self.loop.asyncio_loop.set_debug(True)

    def _gather_handlers(self):
        handlers = list(self.context.urlspecs)
        self.context.msg.emit("gather_http_handlers", handlers)
        assert(all(isinstance(h, URLSpec) for h in handlers))
        return handlers

    def run(self):
        logger.info("Listening on port %d", self.port)
        self.app.listen(self.port)
        self.context.msg.emit("startup")
        self.loop.start()

    @property
    def port(self):
        return self.context.port

    @property
    def env(self):
        return self.context.env
