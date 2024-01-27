from datetime import datetime, timedelta, timezone
import io
import math

import matplotlib.pyplot as pyplot
from moviepy.editor import VideoFileClip
import numpy
import PIL.ExifTags
import PIL.Image
from pydub import AudioSegment
from sqlalchemy.orm import Session

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
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            video = VideoFileClip(fh)
            preview_frame = PIL.Image.fromarray(video.get_frame(0))
            video.close()
        preview_frame.thumbnail((PREVIEW_MAX_W, PREVIEW_MAX_H))
        self.__generate_previews(asset, preview_frame)
        preview_frame.close()

    def __update_audio_previews(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.AUDIO
        assert asset.file is not None
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            audio = AudioSegment.from_file(fh)
            num_channels = audio.channels
            data = numpy.array(audio.get_array_of_samples())
            del audio
        # collapse to mono
        if num_channels == 2:
            data = data.reshape((-1, 2))
            data = data.sum(axis=1) / 2
        # downsample
        data = data[::int(len(data)/50000)]
        # plot
        figure, axes = pyplot.subplots(figsize=(PREVIEW_MAX_H/100, PREVIEW_MAX_H/100), dpi=100)
        axes.plot(data, color='#3b7aaa', linewidth=2)
        axes.fill_between(range(len(data)), data, color='#3b7aaa', alpha=0.3)
        del data
        axes.set_axis_off()
        figure.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        axes.margins(0, 0)
        buffer = io.BytesIO()
        figure.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
        buffer.seek(0)
        wave_preview = PIL.Image.open(buffer)
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

    def __update_photo_metadata(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.PHOTO
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

    def __update_video_metadata(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.VIDEO
        assert asset.file is not None
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            video = VideoFileClip(fh)
            asset.width = video.w
            asset.height = video.h
            asset.fps = video.fps
            asset.duration = video.duration
            video.close()
    
    def __update_audio_metadata(self, asset: PhotoAsset):
        assert asset.kind == PhotoAssetKind.AUDIO
        assert asset.file is not None
        with self.contents.open(asset.file, OpenMode.READ) as fh:
            audio = AudioSegment.from_file(fh)
            asset.duration = len(audio) / 1000.0
            # convert bits per sec to kbps
            asset.bitrate = audio.frame_rate * audio.sample_width * 8 * audio.channels / 1000

    def update_metadata(self, asset: PhotoAsset):
        match asset.kind:
            case PhotoAssetKind.PHOTO:
                return self.__update_photo_metadata(asset)
            case PhotoAssetKind.VIDEO:
                return self.__update_video_metadata(asset)
            case PhotoAssetKind.AUDIO:
                return self.__update_audio_metadata(asset)
            case _:
                raise ValueError(f"Unknown asset kind '{asset.kind}'")
