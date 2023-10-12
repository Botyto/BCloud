from sqlalchemy.orm import Session
from uuid import UUID

from .data import FileMetadata
from .tools.files import FileManager

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.handlers import AuthError
from core.graphql.result import SuccessResult
from core.miniapp.sql import MiniappSqlEvent


class FilesModule(GqlMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = FileManager(self.context.files, self.user_id, self.session)
        return self._manager
    
    @query()
    def by_path(self, path: str, follow_last_link: bool = True) -> FileMetadata|None:
        return self.manager.by_path(path, follow_last_link=follow_last_link)

    @query()
    def by_id(self, id: UUID) -> FileMetadata|None:
        return self.manager.by_id(id)
    
    @query()
    def exists(self, path: str) -> SuccessResult:
        return SuccessResult(self.manager.exists(path))
    
    @mutation()
    def makefile(self, path: str, mime_type: str|None = None) -> FileMetadata:
        file = self.manager.makefile(path, mime_type=mime_type)
        self.log_activity("files.new", {"path": path, "type": "file"})
        return file
    
    @mutation()
    def copyfile(self, src: str, dst: str) -> FileMetadata:
        file = self.manager.copyfile(src, dst)
        self.log_activity("files.copy", {"src": src, "dst": dst, "type": file.isfile and "file" or "dir"})
        return file
    
    @mutation()
    def makedirs(self, path: str) -> FileMetadata:
        dir = self.manager.makedirs(path)
        self.log_activity("files.new", {"path": path, "type": "dir"})
        return dir
    
    @mutation()
    def makelink(self, path: str, target: str) -> FileMetadata:
        link = self.manager.makelink(path, target)
        self.log_activity("files.new", {"path": path, "target": target, "type": "link"})
        return link
    
    @mutation()
    def delete(self, path: str) -> SuccessResult:
        self.manager.delete(path)
        self.log_activity("files.delete", {"path": path})
        return SuccessResult()
    
    @mutation()
    def rename(self, src: str, dst: str) -> FileMetadata:
        self.log_activity("files.rename", {"src": src, "dst": dst})
        return self.manager.rename(src, dst)



class DeleteFileEvent(MiniappSqlEvent):
    TARGET = Session
    IDENTIFIER = "before_flush"

    def run(self, session: Session, flush_context, instances):
        manager: FileManager|None = None
        for entity in session.deleted:
            if not isinstance(entity, FileMetadata):
                continue
            if manager is None:
                manager = FileManager.without_user(self.context.files, session)
            manager.contents.delete(entity)
