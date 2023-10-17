import dataclasses
import io
import PIL.Image

from . import format as fmt
from .transcoder import Transcoder, ParamDef, TranscodeContext


@dataclasses.dataclass
class PILFormat:
    format: fmt.Format
    pil_name: str

PIL_INPUT_OUTPUT_FORMATS = [
    PILFormat(fmt.IMAGE_BMP, "BMP"),
    PILFormat(fmt.IMAGE_DDS, "DDS"),
    PILFormat(fmt.IMAGE_GIF, "GIF"),
    PILFormat(fmt.IMAGE_ICO, "ICO"),
    PILFormat(fmt.IMAGE_JPEG, "JPEG"),
    PILFormat(fmt.IMAGE_JPEG2000, "JPEG2000"),
    PILFormat(fmt.IMAGE_PNG, "PNG"),
    PILFormat(fmt.IMAGE_PPM, "PPM"),
    PILFormat(fmt.IMAGE_TGA, "TGA"),
    PILFormat(fmt.IMAGE_TIFF, "TIFF"),
    PILFormat(fmt.IMAGE_WEBP, "WEBP"),
]

PIL_INPUT_FORMATS = [
    PILFormat(fmt.IMAGE_CUR, "CUR"),
    PILFormat(fmt.IMAGE_PIXAR, "PIXAR"),
    PILFormat(fmt.IMAGE_PSD, "PSD"),
    *PIL_INPUT_OUTPUT_FORMATS,
]

PIL_OUTPUT_FORMATS = [
    PILFormat(fmt.DOCUMENT_PDF, "PDF"),
    *PIL_INPUT_OUTPUT_FORMATS,
]

PIL_PARAMS = [
    ParamDef.make_float("quality", 0.0, 1.0, 1.0),
]

for src_format in PIL_INPUT_FORMATS:
    for dst_format in PIL_OUTPUT_FORMATS:
        if src_format == dst_format:
            continue
        max_quality = 95 if dst_format.format == fmt.IMAGE_JPEG else 100
        def pil_transcode(context: TranscodeContext) -> bytes:
            context.set_progress(0.0)
            input = io.BytesIO()
            input.write(context.data)
            context.set_progress(0.33)
            img = PIL.Image.open(input)
            context.set_progress(0.66)
            result = io.BytesIO()
            input_quality = context.params.get("quality")
            quality = int(input_quality * max_quality) if input_quality is not None else max_quality
            img.save(result, format=dst_format.pil_name, quality=quality)
            result = result.getvalue()
            context.set_progress(1.0)
            return result
        Transcoder(src_format.format, dst_format.format, PIL_PARAMS, pil_transcode, True)
