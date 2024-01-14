from uuid import UUID

from sqlalchemy.orm import InstrumentedAttribute

from core.api.modules.rest import RestMiniappModule, get, post, ApiResponse

from .data import PhotoAsset
from .tools.asset import PhotoAssetManager
from .tools.files import PhotoFileManager, FileMetadata


class ContentsModule(RestMiniappModule):
    _assets: PhotoAssetManager
    _files: PhotoFileManager

    @property
    def assets(self) -> PhotoAssetManager:
        if self._assets is None:
            self._assets = PhotoAssetManager(self.user_id, self.context, self.session)
        return self._assets

    @property
    def files(self):
        if self._files is None:
            self._files = PhotoFileManager(self.user_id, self.context, self.session)
        return self._files
    
    def _read(self, asset_id: str, attr: InstrumentedAttribute[FileMetadata|None]):
        asset = self.assets.get(UUID(asset_id))
        file: FileMetadata = getattr(asset, attr.key)
        if file is None:
            raise FileNotFoundError()
        response = ApiResponse()
        if file.mime_type is not None:
            response.add_header("Content-Type", file.mime_type)
        response.content = self.files.read(asset)
        return response

    @get("/api/photos/contents/(.*)", name="photos.contents.read")
    def content_read(self, asset_id: str):
        return self._read(asset_id, PhotoAsset.file)

    @post("/api/photos/contents/(.*)", name="photos.contents.write")
    def content_write(self, asset_id: str):
        asset = self.assets.get(UUID(asset_id))
        mime_type = self.request.headers.get("Content-Type", "application/octet-stream")
        self.files.write(asset, self.request.body, mime_type)

    @get("/api/photos/preview/(.*)", name="photos.preview.read")
    def preview_read(self, asset_id: str):
        return self._read(asset_id, PhotoAsset.preview)
    
    @get("/api/photos/thumbnail/(.*)", name="photos.thumbnail.read")
    def thumbnail_read(self, asset_id: str):
        return self._read(asset_id, PhotoAsset.thumbnail)
