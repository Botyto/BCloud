from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import logging
import requests
from typing import List, Dict
from uuid import UUID

from core.data.sql.database import Session

from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext
from miniapps.profile.importing.google_items import GoogleItem, GoogleItemContext, GoogleItemImporter

from .data import PhotoAsset, PhotoAssetKind, PhotoAlbumKind
from .tools.album import PhotoAlbumManager
from .tools.asset import PhotoAssetManager
from .tools.files import PhotoFileManager

logger = logging.getLogger(__name__)


class GPhotoType(Enum):
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"


class GVideoStatus(Enum):
    UNSPECIFIED = "UNSPECIFIED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass
class GPhotoMetadata:
    creation_time: datetime
    width: int
    height: int
    camera_make: str
    camera_model: str
    media_type: GPhotoType
    # photo metadata
    focal_length: float|None
    aperature_f: float|None
    iso: int|None
    exposure_time: float|None
    # video metadata
    fps: int|None
    status: GVideoStatus|None

    @classmethod
    def _parse_datetime(cls, timestamp: str):
        # RFC3339 UTC "2014-10-02T15:01:23Z"
        return datetime.fromisoformat(timestamp[:-1]).replace(tzinfo=timezone.utc)

    @classmethod
    def photo(cls, raw_meta: dict):
        return cls(
            creation_time=cls._parse_datetime(raw_meta["creationTime"]),
            width=raw_meta["width"],
            height=raw_meta["height"],
            camera_make=raw_meta["photo"]["cameraMake"],
            camera_model=raw_meta["photo"]["cameraModel"],
            media_type=GPhotoType.PHOTO,
            focal_length=raw_meta["photo"]["focalLength"],
            aperature_f=raw_meta["photo"]["apertureFNumber"],
            iso=raw_meta["photo"]["isoEquivalent"],
            exposure_time=raw_meta["photo"]["exposureTime"],
            fps=None,
            status=None,
        )
    
    @classmethod
    def video(cls, raw_meta: dict):
        return cls(
            creation_time=cls._parse_datetime(raw_meta["creationTime"]),
            width=raw_meta["width"],
            height=raw_meta["height"],
            camera_make=raw_meta["video"]["cameraMake"],
            camera_model=raw_meta["video"]["cameraModel"],
            media_type=GPhotoType.VIDEO,
            focal_length=None,
            aperature_f=None,
            iso=None,
            exposure_time=None,
            fps=raw_meta["video"]["fps"],
            status=GVideoStatus(raw_meta["video"]["status"]),
        )

    @classmethod
    def from_response(cls, item: dict):
        is_photo = "photo" in item
        raw_metadata = item["mediaMetadata"]
        return cls.photo(raw_metadata) if is_photo else cls.video(raw_metadata)


@dataclass
class GPhotoContributor:
    profile_picture_base_url: str
    display_name: str

    @classmethod
    def from_response(cls, item: dict|None):
        if item is None:
            return
        return cls(
            profile_picture_base_url=item["contributorInfo"]["profilePictureBaseUrl"],
            display_name=item["contributorInfo"]["displayName"],
        )

@dataclass
class GPhoto(GoogleItem):
    id: str
    description: str
    product_url: str
    base_url: str
    mime_type: str
    metadata: GPhotoMetadata
    contributor: GPhotoContributor|None
    filename: str

    @property
    def google_name(self):
        return self.filename
    
    @classmethod
    def from_response(cls, item: dict):
        return cls(
            id=item["id"],
            description=item["description"],
            product_url=item["productUrl"],
            base_url=item["baseUrl"],
            mime_type=item["mimeType"],
            metadata=GPhotoMetadata.from_response(item["mediaMetadata"]),
            contributor=GPhotoContributor.from_response(item.get("contributorInfo")),
            filename=item["filename"],
        )


@dataclass
class PhotoHelper:
    assets: PhotoAssetManager
    files: PhotoFileManager


class PhotoItemImporter(GoogleItemImporter[GPhoto, PhotoHelper]):
    ITEM_NAME = "photo"
    PAGINATED = True

    mapping: Dict[str, UUID]
    _internal_mapping: Dict[str, PhotoAsset]

    def __init__(self, logger: logging.Logger, context: GoogleImportingContext, mapping: Dict[str, UUID]):
        super().__init__(logger, context)
        self.mapping = mapping
        self._internal_mapping = dict()

    def gather_page_next(self, page_token: str|None):
        return self.context.service.photos().list(filter="", pageSize=100, pageToken=page_token).execute()
    
    def gather_page_process(self, output: List[GPhoto], response: dict):
        items = response.get("mediaItems", [])
        for item in items:
            photo = GPhoto.from_response(item)
            output.append(photo)

    def create_helper(self, session: Session):
        return PhotoHelper(
            assets=PhotoAssetManager(self.context.user_id, self.context, session),
            files=PhotoFileManager(self.context.user_id, self.context, session),
        )

    def import_item(self, gphoto_context: GoogleItemContext[GPhoto, PhotoHelper]):
        is_photo = gphoto_context.item.metadata.media_type == GPhotoType.PHOTO
        if not is_photo and gphoto_context.item.metadata.status != GVideoStatus.READY:
            self.log.warning(f"Skipping {self.ITEM_NAME} {gphoto_context.item_num} because it is not ready yet")
            return
        asset = gphoto_context.helper.assets.create(PhotoAssetKind.PHOTO if is_photo else PhotoAssetKind.VIDEO)
        asset.created_at_utc = gphoto_context.item.metadata.creation_time
        asset.width = gphoto_context.item.metadata.width
        asset.height = gphoto_context.item.metadata.height
        asset.camera_make = gphoto_context.item.metadata.camera_make
        asset.camera_model = gphoto_context.item.metadata.camera_model
        if is_photo:
            asset.focal_length = gphoto_context.item.metadata.focal_length
            asset.fnumber = gphoto_context.item.metadata.aperature_f
            asset.iso = gphoto_context.item.metadata.iso
            asset.exposure_time = gphoto_context.item.metadata.exposure_time
        else:
            asset.fps = gphoto_context.item.metadata.fps
        download_url = gphoto_context.item.base_url + "=d"
        response = requests.get(download_url)
        if response.status_code != 200:
            self.log.error("Failed to download %s %s: %d %s", self.ITEM_NAME, gphoto_context.item_num, response.status_code, response.reason)
            return
        gphoto_context.helper.files.write(asset, response.content, gphoto_context.item.mime_type)
        gphoto_context.session.commit()
        self._internal_mapping[gphoto_context.item.id] = asset

    def items_created(self, gitems: List[GPhoto], helper: PhotoHelper):
        helper.assets.session.commit()
        for gitem in gitems:
            if gitem.id in self.mapping:
                self.mapping[gitem.id] = self._internal_mapping[gitem.id].id
        del self._internal_mapping


@dataclass
class GAlbumShareOptions:
    is_collaborative: bool
    is_commentable: bool

    @classmethod
    def from_response(cls, item: dict):
        return cls(
            is_collaborative=item["shareInfo"]["shareableUrl"],
            is_commentable=item["shareInfo"]["shareToken"],
        )


@dataclass
class GAlbumShareInfo:
    options: GAlbumShareOptions
    sherable_url: str
    share_token: str
    is_joined: bool
    is_owned: bool
    is_joinable: bool

    @classmethod
    def from_response(cls, item: dict|None):
        if item is None:
            return
        return cls(
            options=GAlbumShareOptions.from_response(item["sharedAlbumOptions"]),
            sherable_url=item["shareableUrl"],
            share_token=item["shareToken"],
            is_joined=item["isJoined"],
            is_owned=item["isOwned"],
            is_joinable=item["isJoinable"],
        )


@dataclass
class GAlbum(GoogleItem):
    id: str
    title: str
    product_url: str
    is_writable: bool
    is_shared: bool
    share_info: GAlbumShareInfo|None
    media_items_count: int
    media_item_ids: List[str]
    cover_base_url: str
    cover_media_item_id: str

    @classmethod
    def __find_media_items(cls, album_id: str, context: GoogleImportingContext):
        result: List[str] = []
        page_token: str|None = None
        while True:
            response = context.service.mediaItems() \
                .search(albumId=album_id, filter="", pageSize=100, pageToken=page_token) \
                .execute()
            items = response.get("mediaItems", [])
            result.extend(item["id"] for item in items)
            page_token = response.get("nextPageToken")
            if page_token is None or not items:
                break
        return result

    @classmethod
    def from_response(cls, item: dict, context: GoogleImportingContext):
        return cls(
            id=item["id"],
            title=item["title"],
            product_url=item["productUrl"],
            is_writable=item["isWritable"],
            is_shared=False,
            share_info=GAlbumShareInfo.from_response(item.get("shareInfo")),
            media_items_count=item["mediaItemsCount"],
            media_item_ids=cls.__find_media_items(item["id"], context),
            cover_base_url=item["coverPhotoBaseUrl"],
            cover_media_item_id=item["coverPhotoMediaItemId"],
        )


class AlbumItemImporter(GoogleItemImporter[GAlbum, PhotoAlbumManager]):
    ITEM_NAME = "album"
    PAGINATED = True

    mapping: Dict[str, UUID]

    def __init__(self, logger: logging.Logger, context: GoogleImportingContext, mapping: Dict[str, UUID]):
        super().__init__(logger, context)
        self.mapping = mapping

    def gather_page_next(self, page_token: str|None):
        return self.context.service.albums().list(filter="", pageSize=100, pageToken=page_token).execute()
    
    def gather_page_process(self, output: List[GAlbum], response: dict):
        items = response.get("albums", [])
        for item in items:
            album = GAlbum.from_response(item, self.context)
            output.append(album)

    def create_helper(self, session: Session):
        return PhotoAlbumManager(self.context.user_id, self.context, session)

    def import_item(self, galbum_context: GoogleItemContext[GAlbum, PhotoAlbumManager]):
        album_kind = PhotoAlbumKind.SHARED if galbum_context.item.is_shared else PhotoAlbumKind.DEFAULT
        asset_ids = [self.mapping[gasset_id] for gasset_id in galbum_context.item.media_item_ids]
        galbum_context.helper.create(galbum_context.item.title, album_kind, asset_ids)


class SharedAlbumItemImporter(AlbumItemImporter):
    ITEM_NAME = "shared album"

    def gather_page_next(self, page_token: str|None):
        return self.context.service.sharedAlbums().list(filter="", pageSize=100, pageToken=page_token).execute()
    
    def gather_page_process(self, output: List[GAlbum], response: dict):
        super().gather_page_process(output, response)
        for album in output:
            album.is_shared = True


class GooglePhotosImporter(GoogleImporter):
    NAME = "photos"
    SERVICE = "photoslibrary"
    VERSION = "v1"
    SCOPES = {
        "https://www.googleapis.com/auth/photoslibrary.readonly",
        "https://www.googleapis.com/auth/photoslibrary.sharing",
    }

    async def run(self, context: GoogleImportingContext):
        mapping: Dict[str, UUID] = dict()
        photos = PhotoItemImporter(logger, context, mapping)
        await photos.run()
        albums = AlbumItemImporter(logger, context, mapping)
        await albums.run()
        shared_albums = SharedAlbumItemImporter(logger, context, mapping)
        await shared_albums.run()
