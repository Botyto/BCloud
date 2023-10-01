from uuid import UUID

from .tools.files import FileManager

from core.api.modules.rest import RestMiniappModule, get, post, ApiResponse
from core.auth.handlers import AuthError


class ContentsModule(RestMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            if self.user_id is None:
                raise AuthError()
            self._manager = FileManager(self.context.files, self.user_id, self.session)
        return self._manager

    @property
    def contents(self):
        return self.manager.contents

    def _read(self, file_id: str, disposition_fmt: str) -> ApiResponse:
        response = ApiResponse()
        file = self.manager.by_id(UUID(file_id))
        content = self.contents.read(file)
        disposition = disposition_fmt.format(file.name)
        response.set_header("Content-Disposition", disposition)
        if file.mime_type:
            response.set_header("Content-Type", file.mime_type)
        if not content:
            response.set_status(204)
            response.set_header("Content-Length", str(0))
        else:
            response.set_status(200)
            response.set_header("Content-Length", str(len(content)))
            response.write(content)
        return response

    @get("api/files/(.*)/contents", name="files.contents.read")
    def read(self, file_id: str) -> ApiResponse:
        return self._read(file_id, "inline")

    @post("api/files/(.*)/contents", name="files.contents.write")
    def write(self, file_id: str) -> None:
        if self.request.files:
            content = self.request.files["file"][0]["body"]
        else:
            content = self.request.body
        if content is None:
            raise ValueError("No content provided")
        file = self.manager.by_id(UUID(file_id))
        mime_type = self.request.headers.get("Content-Type")
        if mime_type is not None:
            file.mime_type = mime_type
        self.log_activity("files.write", {"path": file.abspath, "mime": file.mime_type})
        self.contents.write(file, content)

    @post("api/files/(.*)/download", name="files.contents.download")
    def download(self, file_id: str) -> ApiResponse:
        return self._read(file_id, "attachment; filename=\"{}\"")
