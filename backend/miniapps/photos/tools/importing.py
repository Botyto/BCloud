from datetime import datetime, timedelta, timezone
import io
import math

from sqlalchemy.orm import Session
import PIL.ExifTags
import PIL.Image

from core.asyncjob.context import AsyncJobContext
from core.data.sql.columns import fit_str

from miniapps.files.tools.contents import OpenMode
from miniapps.files.tools.files import FileManager

from ..data import PhotoAsset, PhotoAssetKind, PhotoAssetOrientation

PREVIEW_MAX_H = 1800  # about 12cm at 440ppi at arms length
PREVIEW_MAX_W = 5*PREVIEW_MAX_H
THUMBNAIL_MAX_H = 900  # about 6cm at 440ppi at arms length
THUMBNAIL_MAX_W = 5*THUMBNAIL_MAX_H
assert THUMBNAIL_MAX_H < PREVIEW_MAX_H
PREVIEW_FORMAT, PREVIEW_MIME = "webp", "image/webp"

def parse_offset_tz(offset_str: str|None):
    if not offset_str:
        return timezone.utc
    positive = True
    sign_str = offset_str[0]
    if sign_str == '-':
        positive = False
        offset_str = offset_str[1:]
    elif sign_str == '+':
        positive = True
        offset_str = offset_str[1:]
    hours = int(offset_str[0:2])
    minutes = int(offset_str[2:4])
    offset = timedelta(hours=hours, minutes=minutes)
    if not positive:
        offset = -offset
    return timezone(offset, name=offset_str)

def nad83_to_nad27(d, m, s):
    sign = math.copysign(1, d)
    return d + sign*m/60 + sign*s/3600

EXIF_ORIENTATIONS = [
    PhotoAssetOrientation.HORIZONTAL,
    PhotoAssetOrientation.MIRROR_HORIZONTAL,
    PhotoAssetOrientation.ROTATE_180,
    PhotoAssetOrientation.MIRROR_VERTICAL,
    PhotoAssetOrientation.MIRROR_HORIZONTAL_ROTATE_270,
    PhotoAssetOrientation.ROTATE_90,
    PhotoAssetOrientation.MIRROR_HORIZONTAL_ROTATE_90,
    PhotoAssetOrientation.ROTATE_270,
]


class PhotoImporter:
    context: AsyncJobContext
    _session: Session|None = None
    _files: FileManager|None = None

    @property
    def session(self):
        if self._session is None:
            self._session = self.context.database.make_session()
        return self._session
    
    @property
    def files(self):
        if self._files is None:
            self._files = FileManager.for_service(self.context.blobs, self.session)
        return self._files
    
    @property
    def contents(self):
        return self.files.contents

    def __init__(self, context: AsyncJobContext, session: Session|None):
        self.context = context
        self._session = session

    def __generate_previews(self, asset: PhotoAsset, image: PIL.Image.Image):
        assert asset.preview is not None
        image.thumbnail((PREVIEW_MAX_W, PREVIEW_MAX_H))
        with io.BytesIO() as preview_bytes:
            image.save(preview_bytes, PREVIEW_FORMAT, quality=80)
            self.contents.write(asset.preview, preview_bytes.getvalue(), PREVIEW_MIME)
        del preview_bytes
        
        assert asset.thumbnail is not None
        image.thumbnail((THUMBNAIL_MAX_W, THUMBNAIL_MAX_H))
        with io.BytesIO() as thumbnail_bytes:
            image.save(thumbnail_bytes, PREVIEW_FORMAT, quality=80)
            self.contents.write(asset.preview, thumbnail_bytes.getvalue(), PREVIEW_MIME)
        del thumbnail_bytes

    def __update_photo_previews(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.PHOTO
        assert asset.file is not None
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            image = PIL.Image.open(fh)
        self.__generate_previews(asset, image)
        image.close()

    def __update_video_previews(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.VIDEO
        assert asset.file is not None
        raise NotImplementedError()
        preview_frame = None  # TODO extract from video
        self.__generate_previews(asset, preview_frame)
        preview_frame.close()

    def __update_audio_previews(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.AUDIO
        assert asset.file is not None
        raise NotImplementedError()
        wave_preview = None  # TODO extract from audio
        self.__generate_previews(asset, wave_preview)
        wave_preview.close()

    def update_previews(self, asset: PhotoAsset):
        match asset.kind:
            case PhotoAssetKind.PHOTO:
                return self.__update_photo_previews(asset)
            case PhotoAssetKind.VIDEO:
                return self.__update_video_previews(asset)
            case PhotoAssetKind.AUDIO:
                return self.__update_audio_previews(asset)
            case _:
                raise ValueError(f"Unknown asset kind '{asset.kind}'")

    def update_exif_info(self, asset: PhotoAsset):
        if asset.kind != PhotoAssetKind.PHOTO:
            return
        assert asset.file is not None
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            image = PIL.Image.open(fh)
        exif: dict = image._getexif()  # type: ignore
        if exif is None:
            return
        asset.width = exif.get(PIL.ExifTags.Base.ImageWidth, image.width)
        asset.height = exif.get(PIL.ExifTags.Base.ImageLength, image.height)
        taken_at_str = exif.get(PIL.ExifTags.Base.DateTimeOriginal)
        if taken_at_str is not None:
            taken_at_tz_offset = exif.get(PIL.ExifTags.Base.OffsetTimeOriginal)
            taken_at_tz = parse_offset_tz(taken_at_tz_offset)
            asset.taken_at_utc = datetime \
                .strptime(taken_at_str, "%Y:%m:%d %H:%M:%S") \
                .replace(tzinfo=taken_at_tz)
        camera_make = exif.get(PIL.ExifTags.Base.Make)
        camera_model = exif.get(PIL.ExifTags.Base.Model)
        software = exif.get(PIL.ExifTags.Base.Software)
        asset.camera_make = camera_make and fit_str(camera_make, PhotoAsset.camera_make)
        asset.camera_model = camera_model and fit_str(camera_model, PhotoAsset.camera_model)
        asset.software = software and fit_str(software, PhotoAsset.software)
        orientation = exif.get(PIL.ExifTags.Base.Orientation)
        if isinstance(orientation, int):
            asset.orientation = EXIF_ORIENTATIONS[orientation - 1]
        asset.fnumber = exif.get(PIL.ExifTags.Base.FNumber)
        asset.exposure_time = exif.get(PIL.ExifTags.Base.ExposureTime)
        asset.iso = exif.get(PIL.ExifTags.Base.ISOSpeedRatings)
        asset.focal_length = exif.get(PIL.ExifTags.Base.FocalLength)
        gpsinfo: dict|None = exif.get(PIL.ExifTags.Base.GPSInfo)
        if gpsinfo is not None:
            latitude_ref = gpsinfo.get(PIL.ExifTags.GPS.GPSLatitudeRef)
            latitude = gpsinfo.get(PIL.ExifTags.GPS.GPSLatitude)
            longitude_ref = gpsinfo.get(PIL.ExifTags.GPS.GPSLongitudeRef)
            longitude = gpsinfo.get(PIL.ExifTags.GPS.GPSLongitude)
            altitude_ref = gpsinfo.get(PIL.ExifTags.GPS.GPSAltitudeRef)
            altitude = gpsinfo.get(PIL.ExifTags.GPS.GPSAltitude)
            if latitude_ref and latitude and longitude_ref and longitude:
                latitude = nad83_to_nad27(*latitude)
                if latitude_ref == 'S':
                    latitude = -latitude
                asset.latitude = latitude
                longitude = nad83_to_nad27(*longitude)
                if longitude_ref == 'W':
                    longitude = -longitude
                asset.longitude = longitude
            if altitude_ref and altitude:
                if altitude_ref[0] == 1:
                    altitude = -altitude
                asset.altitude = altitude
