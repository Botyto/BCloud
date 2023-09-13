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
        logger.info("Running app...")
