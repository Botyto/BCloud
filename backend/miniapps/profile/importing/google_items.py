import logging
import pickle
from typing import Generic, List, TypeVar

from core.data.blobs.base import OpenMode
from core.data.sql.database import Session

from .google import GoogleImportingContext


class GoogleItem:
    @property
    def google_name(self):
        raise NotImplementedError()

HelperType = TypeVar("HelperType")
ItemType = TypeVar("ItemType", bound=GoogleItem)


class GoogleItemContext(GoogleImportingContext, Generic[ItemType, HelperType]):
    i: int
    n: int
    session: Session
    manager: HelperType|None
    item: ItemType

    def __init__(self, base: GoogleImportingContext, i: int, n: int, session: Session, helper: HelperType|None, item: ItemType):
        self._extend(base)
        self.i = i
        self.n = n
        self.session = session
        self.manager = helper
        self.item = item

    @property
    def item_num(self):
        return f"{self.i + 1}/{self.n}"


class GoogleItemImporter(Generic[ItemType, HelperType]):
    ITEM_NAME: str
    PAGINATED: bool = False

    log: logging.Logger
    context: GoogleImportingContext

    def __init__(self, logger: logging.Logger, context: GoogleImportingContext):
        self.log = logger
        self.context = context

    def gather(self, output: List[ItemType]):
        if self.PAGINATED:
            self.__gather_paginated(output)
        else:
            raise NotImplementedError()
    
    def gather_page_next(self, page_token: str|None):
        raise NotImplementedError()
    
    def gather_page_process(self, output: List[ItemType], response: dict):
        raise NotImplementedError()
    
    def create_helper(self, session: Session) -> HelperType|None:
        pass

    def import_item(self, gitem_context: GoogleItemContext[ItemType, HelperType]):
        raise NotImplementedError()
    
    def __gather_paginated(self, output: List[ItemType]):
        page_token: str|None = None
        while True:
            response = self.gather_page_next(page_token)
            old_len = len(output)
            self.gather_page_process(output, response)
            new_len = len(output)
            page_token = response.get("nextPageToken")
            if page_token is None or old_len == new_len:
                break

    def __create_items(self, gitems: List[ItemType]):
        self.log.debug("Importing %d %s", len(gitems), self.ITEM_NAME)
        with self.context.database.make_session() as session:
            manager = self.create_helper(session)
            for i, gitem in enumerate(gitems):
                gitem_context = GoogleItemContext(self.context, i, len(gitems), session, manager, gitem)
                self.__import_item(gitem_context)

    def __import_item(self, context: GoogleItemContext[ItemType, HelperType]):
        self.log.debug("Importing %s %s - %s", self.ITEM_NAME, context.item_num, context.item.google_name)
        try:
            self.import_item(context)
        except Exception as e:
            self.log.debug("Failed to import %s %s", self.ITEM_NAME, context.item_num)
            self.log.exception(e)

    async def run(self):
        items: List[ItemType] = []
        cache_addr = self.context.temp_file_addr(f"g{self.ITEM_NAME}_import", f"{self.ITEM_NAME}.pickle")
        if self.context.blobs.exists(cache_addr):
            self.log.debug("Loading cache...")
            with self.context.blobs.open(cache_addr, OpenMode.READ) as fh:
                items = pickle.load(fh)
        else:
            self.log.debug("Gethering...")
            self.gather(items)
            with self.context.blobs.open(cache_addr, OpenMode.WRITE) as fh:
                pickle.dump(items, fh)
        self.__create_items(items)
        self.log.debug("Finished importing")
        # TODO delete cache file
