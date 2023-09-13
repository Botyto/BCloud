import logging

from core.data.context import DataContext

logger = logging.getLogger(__name__)


class AppContext(DataContext):
    pass


class App:
    context: AppContext

    def __init__(self, context: AppContext):
        self.context = context

    def run(self):
        logger.info("Running app...")
