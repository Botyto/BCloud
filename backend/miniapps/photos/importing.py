from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import logging
from typing import List

from miniapps.profile.importing.google import GoogleImporter, GoogleImportingContext
from miniapps.profile.importing.google_items import GoogleItem, GoogleItemContext, GoogleItemImporter

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


@dataclass
class GPhotoContributor:
    profile_picture_base_url: str
    display_name: str


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


class PhotoItemImporter(GoogleItemImporter[GPhoto, None]):
    ITEM_NAME = "photo"
    PAGINATED = True

    def gather_page_next(self, page_token: str|None):
        return self.context.service.photos().list(filter="", pageSize=100, pageToken=page_token).execute()
    
    def gather_page_process(self, output: List[GPhoto], response: dict):
        items = response.get("mediaItems", [])
        for item in items:
            is_photo = "photo" in item["mediaMetadata"]
            raw_metadata = item["mediaMetadata"]
            metadata = GPhotoMetadata.photo(raw_metadata) if is_photo else GPhotoMetadata.video(raw_metadata)
            contributor: GPhotoContributor|None = None
            if "contributorInfo" in item:
                contributor = GPhotoContributor(
                    profile_picture_base_url=item["contributorInfo"]["profilePictureBaseUrl"],
                    display_name=item["contributorInfo"]["displayName"],
                )
            note = GPhoto(
                id=item["id"],
                description=item.get("description", ""),
                product_url=item["productUrl"],
                base_url=item["baseUrl"],
                mime_type=item["mimeType"],
                metadata=metadata,
                contributor=contributor,
                filename=item["filename"],
            )
            output.append(note)

    def import_item(self, gphoto_context: GoogleItemContext[GPhoto, None]):
        raise NotImplementedError()


@dataclass
class GAlbumShareOptions:
    is_collaborative: bool
    is_commentable: bool


@dataclass
class GAlbumShareInfo:
    options: GAlbumShareOptions
    sherable_url: str
    share_token: str
    is_joined: bool
    is_owned: bool
    is_joinable: bool


@dataclass
class GAlbum(GoogleItem):
    id: str
    title: str
    product_url: str
    is_writable: bool
    share_info: GAlbumShareInfo
    media_items_count: int
    cover_base_url: str
    cover_media_item_id: str


class AlbumItemImporter(GoogleItemImporter[GAlbum, None]):
    pass


class GooglePhotosImporter(GoogleImporter):
    NAME = "photos"
    SERVICE = "photoslibrary"
    VERSION = "v1"
    SCOPES = {
        "https://www.googleapis.com/auth/photoslibrary.readonly",
    }

    async def run(self, context: GoogleImportingContext):
        photos = PhotoItemImporter(logger, context)
        await photos.run()
