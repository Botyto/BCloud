from dataclasses import dataclass
import logging
from typing import Any, List

from core.data.sql.database import Session

from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext
from miniapps.profile.importing.google_items import GoogleItem, GoogleItemContext, GoogleItemImporter

from .data import NotesCollection, NotesNote, NotesCollectionView, NotesFileKind
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
class GNote(GoogleItem):
    name: str
    title: str
    content: str
    checklist: List[GNoteListItem]
    trashed: bool
    attachments: List[GNoteAttachment]

    @property
    def google_name(self):
        return self.name


@dataclass
class NoteHelper:
    manager: NotesManager
    collection: NotesCollection


# As of writing this, the Google Keep API is intended only for enterprise users.
# This question mentions a link to a ticket addressing this:
# https://stackoverflow.com/questions/70312083/google-keep-api-responds-with-invalid-scope-when-using-documented-scopes
class KeepItemImporter(GoogleItemImporter):
    def gather_page_next(self, page_token: str|None):
        return self.context.service.notes().list(filter="", pageSize=100, pageToken=page_token).execute()
    
    def __parse_list_item(self, item: Any) -> GNoteListItem:
        children = []
        if "childListItems" in item:
            children = [self.__parse_list_item(i) for i in item["childListItems"]]
        return GNoteListItem(
            text=item["text"]["text"],
            checked=item["checked"],
            children=children,
        )

    def gather_page_process(self, output: List[GNote], response: dict):
        items = response.get("notes", [])
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

    COLLECTION_NAME = "Google Keep"
    def __get_gkeep_collection(self, session: Session):
        collections = CollectionsManager(self.context.user_id, session)
        gkeep_collections = collections.by_name(self.COLLECTION_NAME, True)
        if gkeep_collections:
            return gkeep_collections[0]  # type: ignore
        return collections.create(self.COLLECTION_NAME, None, NotesCollectionView.NOTES)

    def create_helper(self, session: Session):
        return NoteHelper(
            manager=NotesManager(self.context.user_id, self.context, session),
            collection=self.__get_gkeep_collection(session),
        )
    
    def __checklist_to_md(self, checklist: List[GNoteListItem], indent: int = 0) -> str:
        output = []
        for item in checklist:
            indent_str = "  " * indent
            checkbox_str = "[x]" if item.checked else "[ ]"
            output.append(f"{indent_str}- {checkbox_str} {item.text}")
            output.extend(self.__checklist_to_md(item.children, indent + 1))
        return "\n".join(output)

    def __download_attachment(self, gnote_context: GoogleItemContext[GNote, NoteHelper], gattachment: GNoteAttachment, note: NotesNote):
        content = gnote_context.service.media() \
            .download_media(name=gattachment.name, mimeType=gattachment.mime_type) \
            .execute()
        gnote_context.helper.manager.files.default_write(note.id, content, gattachment.mime_type, NotesFileKind.ATTACHMENT)

    def import_item(self, gnote_context: GoogleItemContext[GNote, NoteHelper]):
        if gnote_context.item.checklist:
            content = self.__checklist_to_md(gnote_context.item.checklist)
        else:
            content = gnote_context.item.content
        note = gnote_context.helper.manager.create(
            collection_id_or_slug=gnote_context.helper.collection.id,
            title=gnote_context.item.title,
            content=content,
            tags=[],
        )
        note.archived = gnote_context.item.trashed
        for i, gattachment in enumerate(gnote_context.item.attachments):
            self.__download_attachment(gnote_context, gattachment, note)
            if i > 1:
                logger.warning("Note %s - %s has more than 1 attachment", gnote_context.item_num, gnote_context.item.google_name)
                break


class GoogleKeepImporter(GoogleImporter):
    NAME = "keep"
    SERVICE = "keep"
    VERSION = "v1"
    SCOPES = {
        "https://www.googleapis.com/auth/keep.readonly",
    }

    async def run(self, context: GoogleImportingContext):
        keep = KeepItemImporter(logger, context)
        await keep.run()
