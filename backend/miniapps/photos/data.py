from datetime import datetime
import enum
from uuid import UUID as PyUUID, uuid4
from typing import List

from core.auth.access import AccessLevel, access_info
from core.auth.data import User
from core.data.sql.columns import DateTime, Enum, Float, Integer, String, UUID, STRING_MAX, utcnow_tz
from core.data.sql.columns import mapped_column, relationship, Mapped, ForeignKey
from core.data.sql.database import Model
from core.data.sql.slugs import SLUG_LENGTH, slug_info

from miniapps.files.data import FileMetadata


class PhotoAssetKind(enum.Enum):
    PHOTO = "PHOTO"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"


class PhotoAssetOrientation(enum.Enum):
    HORIZONTAL = "HORIZONTAL"
    MIRROR_HORIZONTAL = "MIRROR_HORIZONTAL"
    ROTATE_180 = "ROTATE_180"
    MIRROR_VERTICAL = "MIRROR_VERTICAL"
    MIRROR_HORIZONTAL_ROTATE_270 = "MIRROR_HORIZONTAL_ROTATE_270"
    ROTATE_90 = "ROTATE_90"
    MIRROR_HORIZONTAL_ROTATE_90 = "MIRROR_HORIZONTAL_ROTATE_90"
    ROTATE_270 = "ROTATE_270"


class PhotoAsset(Model):
    __tablename__ = "PhotoAsset"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped[User] = relationship(User, backref="photos")
    kind: Mapped[PhotoAssetKind] = mapped_column(Enum(PhotoAssetKind), nullable=False)
    origin_id: Mapped[PyUUID] = mapped_column(ForeignKey("PhotoAsset.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True, default=None)
    origin: Mapped["PhotoAsset"] = relationship("PhotoAsset", remote_side=[id])
    derived_assets: Mapped[List["PhotoAsset"]] = relationship("PhotoAsset", back_populates="origin")
    tags: Mapped[List["PhotoTag"]] = relationship(secondary="PhotoAssetTagAssoc")
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow_tz)
    album_entries: Mapped[List["PhotoAlbumEntry"]] = relationship("PhotoAlbumEntry", back_populates="asset")
    cover_of_albums: Mapped[List["PhotoAlbum"]] = relationship("PhotoAlbum", back_populates="cover_asset")
    # contents
    file_id: Mapped[PyUUID|None] = mapped_column(ForeignKey(FileMetadata.id), nullable=True)
    file: Mapped[FileMetadata|None] = relationship("FileMetadata", backref="photo_asset", lazy="joined", foreign_keys=[file_id])
    preview_id: Mapped[PyUUID|None] = mapped_column(ForeignKey(FileMetadata.id), nullable=True)
    preview: Mapped[FileMetadata|None] = relationship("FileMetadata", backref="preview_of_photo", lazy="joined", foreign_keys=[preview_id])
    thumbnail_id: Mapped[PyUUID|None] = mapped_column(ForeignKey(FileMetadata.id), nullable=True)
    thumbnail: Mapped[FileMetadata|None] = relationship("FileMetadata", backref="thumbnail_of_photo", lazy="joined", foreign_keys=[thumbnail_id])
    # metadata
    width: Mapped[float] = mapped_column(Float, default=None, nullable=True)
    height: Mapped[float] = mapped_column(Float, default=None, nullable=True)
    taken_at_utc: Mapped[datetime|None] = mapped_column(DateTime, default=None, nullable=True)
    camera_make: Mapped[str|None] = mapped_column(String(512), default=None, nullable=True)
    camera_model: Mapped[str|None] = mapped_column(String(512), default=None, nullable=True)
    software: Mapped[str|None] = mapped_column(String(512), default=None, nullable=True)
    orientation: Mapped[PhotoAssetOrientation] = mapped_column(Enum(PhotoAssetOrientation), default=None, nullable=True)
    fnumber: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    exposure_time: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    iso: Mapped[int|None] = mapped_column(Integer, default=None, nullable=True)
    focal_length: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    latitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    longitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    altitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)


class PhotoAssetTagAssoc(Model):
    __tablename__ = "PhotoAssetTagAssoc"
    asset_id: Mapped[PyUUID] = mapped_column(ForeignKey(PhotoAsset.id), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("PhotoTag.id"), primary_key=True)


class PhotoTag(Model):
    __tablename__ = "PhotoTag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    assets: Mapped[List[PhotoAsset]] = relationship(secondary="PhotoAssetTagAssoc", viewonly=True)


class PhotoAlbumEntryKind(enum.Enum):
    ASSET = "ASSET"
    LOCATION = "LOCATION"
    MAP = "MAP"
    TEXT = "TEXT"


class PhotoAlbumEntry(Model):
    __tablename__ = "PhotoAlbumEntry"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sort_key: Mapped[int] = mapped_column(Integer, nullable=False)
    album_id: Mapped[PyUUID] = mapped_column(ForeignKey("PhotoAlbum.id"), nullable=False)
    album: Mapped["PhotoAlbum"] = relationship("PhotoAlbum", back_populates="entries")
    kind: Mapped[PhotoAlbumEntryKind] = mapped_column(Enum(PhotoAlbumEntryKind), nullable=False)
    asset_id: Mapped[PyUUID] = mapped_column(ForeignKey(PhotoAsset.id))
    asset: Mapped[PhotoAsset] = relationship(PhotoAsset, back_populates="album_entries")
    text: Mapped[str|None] = mapped_column(String(STRING_MAX), default=None, nullable=True)
    src_latitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    src_longitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    dst_latitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)
    dst_longitude: Mapped[float|None] = mapped_column(Float, default=None, nullable=True)


class PhotoAlbumKind(enum.Enum):
    DEFAULT = "DEFAULT"
    SHARED = "SHARED"


class PhotoAlbum(Model):
    __tablename__ = "PhotoAlbum"
    id: Mapped[PyUUID] = mapped_column(UUID, primary_key=True, default=uuid4)
    user_id: Mapped[PyUUID] = mapped_column(ForeignKey(User.id), nullable=False)
    user: Mapped[User] = relationship(User, backref="albums")
    kind: Mapped[PhotoAlbumKind] = mapped_column(Enum(PhotoAlbumKind), nullable=False)
    created_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow_tz)
    access: Mapped[AccessLevel] = mapped_column(Enum(AccessLevel), nullable=False, default=AccessLevel.PRIVATE, info=access_info())
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(SLUG_LENGTH), nullable=False, info=slug_info())
    entries: Mapped[List[PhotoAlbumEntry]] = relationship(PhotoAlbumEntry, back_populates="album")
    cover_asset_id: Mapped[PyUUID|None] = mapped_column(ForeignKey(PhotoAsset.id), nullable=True)
    cover_asset: Mapped[PhotoAsset|None] = relationship(PhotoAsset, back_populates="cover_of_albums")
