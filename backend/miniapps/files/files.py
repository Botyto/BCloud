from uuid import UUID

from .data import FileMetadata
from .tools.files import FileManager

from core.api.modules.gql import GqlMiniappModule, query, mutation
from core.auth.handlers import AuthError
from core.graphql.result import SuccessResult


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
        return self.manager.makefile(path, mime_type=mime_type)
    
    @mutation()
    def copyfile(self, src: str, dst: str) -> FileMetadata:
        return self.manager.copyfile(src, dst)
    
    @mutation()
    def makedirs(self, path: str) -> FileMetadata:
        return self.manager.makedirs(path)
    
    @mutation()
    def makelink(self, path: str, target: str) -> FileMetadata:
        return self.manager.makelink(path, target)
    
    @mutation()
    def delete(self, path: str) -> SuccessResult:
        self.manager.delete(path)
        return SuccessResult()

    @mutation()
    def rename(self, src: str, dst: str) -> FileMetadata:
        return self.manager.rename(src, dst)
