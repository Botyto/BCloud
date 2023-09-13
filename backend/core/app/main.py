import logging

from core.data.context import DataContext

logger = logging.getLogger(__name__)


class AppContext(DataContext):
    def __init__(self, base: DataContext):
        self._extend(base)


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        from core.data.blobs.manager import Address
        self.context.blobs.manager.write(Address.random("app"), b"Hello, world!")
        logger.info("Running app...")
