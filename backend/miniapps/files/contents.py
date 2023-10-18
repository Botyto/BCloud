from .tools import fspath
from .tools.files import FileManager

from core.api.modules.rest import RestMiniappModule, get, post, ApiResponse


class ContentsModule(RestMiniappModule):
    _manager: FileManager|None = None

    @property
    def manager(self):
        if self._manager is None:
            self._manager = FileManager(self.context.files, self.user_id, self.session)
        return self._manager

    @property
    def contents(self):
        return self.manager.contents
    
    def _url_to_path(self, url: str):
        slash_idx = url.find("/")
        if slash_idx < 0:
            return url
        storage_id = url[:slash_idx]
        path = url[slash_idx:]
        return fspath.join(storage_id, path)

    def _read_internal(self, path: str, disposition_fmt: str) -> ApiResponse:
        response = ApiResponse()
        file = self.manager.by_path(path)
        if file is None:
            response.set_status(404)
            return response
        try:
            content = self.contents.read(file)
        except FileNotFoundError:
            response.set_status(204)
            return response
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

    @get("/api/files/contents/(.*)", name="files.contents.read")
    def read_content(self, path: str) -> ApiResponse:
        path = self._url_to_path(path)
        return self._read_internal(path, "inline")

    @post("/api/files/contents/(.*)", name="files.contents.write")
    def write_content(self, path: str):
        if self.request.files:
            content = self.request.files["file"][0]["body"]
        else:
            content = self.request.body
        if content is None:
            raise ValueError("No content provided")
        path = self._url_to_path(path)
        file = self.manager.by_path(path)
        response = ApiResponse()
        if file is None:
            response.set_status(404)
            return response
        mime_type = self.request.headers.get("Content-Type")
        if mime_type is not None:
            file.mime_type = mime_type
        self.log_activity("files.write", {"path": file.abspath, "mime": file.mime_type, "size": len(content)})
        self.contents.write(file, content)
        return response

    @get("/api/files/download/(.*)", name="files.contents.download")
    def download_content(self, path: str) -> ApiResponse:
        path = self._url_to_path(path)
        return self._read_internal(path, "attachment; filename=\"{}\"")
