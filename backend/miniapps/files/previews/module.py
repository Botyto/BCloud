from .archives import ArchivePreviews, ArchivePreview

from ..tools.files import FileManager

from core.api.modules.gql import GqlMiniappModule, query
from core.auth.handlers import AuthError
from core.data.blobs.base import OpenMode


class PreviewModule(GqlMiniappModule, ArchivePreviews):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = FileManager(self.context.blobs, self.user_id, self.session)
        return self._manager

    @query()
    def archive(self, path: str) -> ArchivePreview:
        file = self.manager.by_path(path)
        if file is None:
            raise FileNotFoundError(path)
        with self.manager.contents.open(file, OpenMode.READ) as blob:
            return self._archive_preview(blob)
