from dataclasses import dataclass
import logging
import pickle
from typing import Any, List

from core.data.sql.database import Session

from core.data.blobs.base import OpenMode
from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext

from .data import NotesCollection, NotesNote
from .tools.collections import CollectionsManager
from .tools.notes import NotesManager

logger = logging.getLogger(__name__)


@dataclass
class GNoteAttachment:
    name: str
    mime_type: str


@dataclass
class GNoteListItem:
    text: str
    checked: bool
    children: List["GNoteListItem"]


@dataclass
class GNote:
    name: str
    title: str
    content: str
    checklist: List[GNoteListItem]
    trashed: bool
    attachments: List[GNoteAttachment]


class KeepNoteContext(GoogleImportingContext):
    i: int
    n: int
    notes: NotesManager
    session: Session
    collection: NotesCollection
    gnote: GNote

    def __init__(self,
        base: GoogleImportingContext,
        i: int, n: int,
        notes: NotesManager,
        session: Session,
        collection: NotesCollection,
        gnote: GNote,
    ):
        self._extend(base)
        self.i = i
        self.n = n
        self.notes = notes
        self.session = session
        self.collection = collection
        self.gnote = gnote

    @property
    def google_name(self):
        return self.gnote.name

    @property
    def note_n(self):
        return f"{self.i + 1}/{self.n}"


# As of writing this, the Google Keep API is intended only for enterprise users.
# This question mentions a link to a ticket addressing this:
# https://stackoverflow.com/questions/70312083/google-keep-api-responds-with-invalid-scope-when-using-documented-scopes
class GoogleKeepImporter(GoogleImporter):
    NAME = "keep"
    SERVICE = "keep"
    VERSION = "v1"
    SCOPES = {
        "https://www.googleapis.com/auth/keep.readonly",
    }

    def __parse_list_item(self, item: Any) -> GNoteListItem:
        children = []
        if "childListItems" in item:
            children = [self.__parse_list_item(i) for i in item["childListItems"]]
        return GNoteListItem(
            text=item["text"]["text"],
            checked=item["checked"],
            children=children,
        )

    def __gather_notes(self, output: list, context: GoogleImportingContext):
        next_page_token: str|None = None
        while True:
            results = context.service.notes().list(filter="", pageSize=100, pageToken=next_page_token).execute()
            next_page_token = results.get("nextPageToken", None)
            items = results.get("notes", [])
            for item in items:
                attachments = [
                    GNoteAttachment(
                        name=att["name"],
                        mime_type=att["mimeType"],
                    )
                    for att in item.get("attachments", [])
                ]
                content: str = ""
                checklist: List[GNoteListItem] = []
                if "text" in item["body"]:
                    content = item["body"]["text"]["text"]
                    checklist = []
                elif "list" in item["body"]:
                    content = ""
                    checklist = [
                        self.__parse_list_item(list_item)
                        for list_item in item["body"]["list"]["listItems"]
                    ]
                note = GNote(
                    name=item["name"],
                    title=item["title"],
                    content=content,
                    checklist=checklist,
                    trashed=item["trashed"],
                    attachments=attachments,
                )
                output.append(note)
            if next_page_token is None or not items:
                break

    COLLECTION_NAME = "Google Keep"
    def __get_gkeep_collection(self, context: GoogleImportingContext, session: Session):
        collections = CollectionsManager(context.user_id, session)
        gkeep_collections = collections.by_name(self.COLLECTION_NAME)
        if gkeep_collections:
            return gkeep_collections[0]  # type: ignore
        return collections.create(self.COLLECTION_NAME)

    def __checklist_to_md(self, checklist: List[GNoteListItem], indent: int = 0) -> str:
        output = []
        for item in checklist:
            indent_str = "  " * indent
            checkbox_str = "[x]" if item.checked else "[ ]"
            output.append(f"{indent_str}- {checkbox_str} {item.text}")
            output.extend(self.__checklist_to_md(item.children, indent + 1))
        return "\n".join(output)

    def __download_attachment(self, context: KeepNoteContext, gattachment: GNoteAttachment, note: NotesNote):
        result = context.service.media().download_media(name=gattachment.name, mimeType=gattachment.mime_type).execute()
        raise NotImplementedError()

    def __import_note(self, context: KeepNoteContext):
        logger.debug("Importing note %s - %s", context.note_n, context.google_name)
        if context.gnote.checklist:
            content = self.__checklist_to_md(context.gnote.checklist)
        else:
            content = context.gnote.content
        note = context.notes.create(
            collection_id=context.collection.id,
            title=context.gnote.title,
            content=content,
            archived=context.gnote.trashed,
        )
        for gattachment in context.gnote.attachments:
            self.__download_attachment(context, gattachment, note)

    def __create_notes(self, gnotes: List[GNote], context: GoogleImportingContext):
        logger.debug("Importing %d notes", len(gnotes))
        with context.database.make_session() as session:
            collection = self.__get_gkeep_collection(context, session)
            notes = NotesManager(context.user_id, session)
            for i, gnote in enumerate(gnotes):
                gnote_context = KeepNoteContext(context, i, len(gnotes), notes, session, collection, gnote)
                self.__import_note(gnote_context)

    async def run(self, context: GoogleImportingContext):
        notes: List[GNote] = []
        cache_addr = context.temp_file_addr("gkeep_import", "notes.pickle")
        if context.blobs.exists(cache_addr):
            logger.debug("Loading cached notes")
            with context.blobs.open(cache_addr, OpenMode.READ) as fh:
                notes = pickle.load(fh)
        else:
            logger.debug("Gethering notes")
            self.__gather_notes(notes, context)
            notes.sort(key=lambda f: f.name)
            with context.blobs.open(cache_addr, OpenMode.WRITE) as fh:
                pickle.dump(notes, fh)
        self.__create_notes(notes, context)
        logger.debug("Finished importing")
        # TODO delete cache file
