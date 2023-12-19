from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy import select
from typing import Any, cast, Dict, List
from uuid import UUID

from .format import Format
from .transcoder import ParamDef, Transcoder, TranscodeContext
from ..tools.files import FileManager
from ..tools.contents import FileContents, NAMESPACE_CONTENT
from ..tools import fspath

from core.api.modules.gql import GqlMiniappModule, mutation, query
from core.asyncjob.data import JobPromise
from core.asyncjob.handlers import AsyncJobHandler


@dataclass
class RunningTranscoder:
    dst_format: Format
    progress: float


class ParamValue:
    id: str
    value: str


class Conversion:
    src: Format
    dst: Format
    params: List[ParamDef]

    def __init__(self, transcoder: Transcoder):
        self.src = transcoder.input
        self.dst = transcoder.output
        self.params = transcoder.params


@dataclass
class JobId:
    job_id: int


class TranscodeModule(GqlMiniappModule):
    @query()
    def available(self, path: str) -> List[Conversion]:
        ext = fspath.ext(path)
        src_format = Format.by_ext(ext)
        if src_format is None:
            return []
        transcoders = Transcoder.by_input(src_format)
        return [Conversion(t) for t in transcoders if t.available()]

    def __parse_params(self, transcoder: Transcoder, values: List[ParamValue]):
        result = {}
        for param_def in transcoder.params:
            input = next(v for v in values if v.id == param_def.id)
            if input is None:
                if param_def.default is None:
                    raise ValueError(f"Missing parameter '{param_def.id}'")
                result[param_def.id] = param_def.default
            else:
                result[param_def.id] = param_def.parse_str(input.value)
        return result

    @mutation()
    def convert(self, path: str, ext: str, params: List[ParamValue]):
        src_ext = fspath.ext(path)
        src_format = Format.by_ext(src_ext)
        if src_format is None:
            raise ValueError(f"Unknown source format '{src_ext}'")
        dst_format = Format.by_ext(ext)
        if dst_format is None:
            raise ValueError(f"Unknown destination format '{ext}'")
        transcoder = Transcoder.find(src_format, dst_format)
        if transcoder is None:
            raise ValueError(f"Conversion from '{src_ext}' to '{ext}' is not supported")
        manager = FileManager(self.context.files, self.user_id, self.session)
        file = manager.by_path(path)
        if file is None:
            raise FileNotFoundError(path)
        parsed_params = self.__parse_params(transcoder, params)
        job_id = self.context.asyncjobs.schedule("files", "transcoding", {
            "file_id": str(file.id),
            "src_ext": src_ext,
            "dst_ext": ext,
            "params": parsed_params,
        })
        self.log_activity("transcode.start", {
            "file_id": str(file.id),
            "file_name": file.name,
            "dst_ext": ext,
        })
        return JobId(job_id)

    @query()
    def running(self, path: str) -> List[RunningTranscoder]:
        statement = select(JobPromise) \
            .where(JobPromise.issuer == "files") \
            .where(JobPromise.type == "transcoding")
        promises = self.session.scalars(statement).all()
        user_id_str = str(self.user_id)
        promises = [p for p in promises if p.payload is not None and p.payload.get("user_id") == user_id_str]
        result = []
        for promise in promises:
            file_path = cast(str, promise.payload.get("file_path"))
            if file_path != path:
                continue
            dst_mime = cast(str, promise.payload.get("dst_mime"))
            state = self.context.asyncjobs.states[promise.id]
            result.append(RunningTranscoder(
                dst_format=Format.by_mime(dst_mime),
                progress=state.progress,
            ))
        return result


class TranscodingHandler(AsyncJobHandler):
    MAX_DURATION_WITHOUT_NOTIFICATION = timedelta(minutes=5)

    def __make_dst_path(self, src_path: str, dst_ext: str, files: FileManager):
        src_ext = fspath.ext(src_path)
        src_no_ext = src_path[:-len(src_ext)]
        return files.unique_name(src_no_ext + dst_ext)

    def run(self):
        params: Dict[str, Any] = self.context.get_payload("params")
        src_ext: str = self.context.get_payload("src_ext")
        src_format = Format.by_ext(src_ext)
        dst_ext: str = self.context.get_payload("dst_ext")
        dst_format = Format.by_ext(dst_ext)
        transcoder = Transcoder.find(src_format, dst_format)
        with self.context.database.make_session() as session:
            files = FileManager.for_service(self.context.files, session)
            file_id = UUID(self.context.get_payload("file_id"))
            src_file = files.by_id(file_id)
            user_id = src_file.user_id
            dst_path = self.__make_dst_path(src_file.abspath, dst_ext, files)
            contents = FileContents(self.context.files, NAMESPACE_CONTENT)
            src_data = contents.read(src_file)
            del contents, src_file, file_id, files
        context = TranscodeContext(self.context, src_data, params)
        start_time = datetime.now()
        dst_data = transcoder.run(context)
        del src_data
        with self.context.database.make_session() as session:
            files = FileManager(self.context.files, user_id, session)
            dst_file = files.makefile(dst_path, dst_format.mime)
            contents = FileContents(self.context.files, NAMESPACE_CONTENT)
            contents.write(dst_file, dst_data)
            del contents, dst_file, files, dst_data, dst_path
        duration = datetime.now() - start_time
        if duration > self.MAX_DURATION_WITHOUT_NOTIFICATION:
            pass  # TODO emit notification
