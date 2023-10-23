from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from .format import Format

from core.asyncjob.context import AsyncJobRuntimeContext


class TranscoderError(Exception):
    pass


class ParamKind(Enum):
    ENUM = "enum"
    STRING = "string"
    FLOAT = "float"


@dataclass
class ParamDef:
    id: str
    kind: ParamKind
    values: List[str]|None = None
    min_value: float|None = None
    max_value: float|None = None
    slider: bool = False
    default: float|str|None = None

    @classmethod
    def make_enum(cls, id: str, values: List[str], default: str|None = None):
        return cls(id, ParamKind.ENUM, values=values, default=default)
    
    @classmethod
    def make_str(cls, id: str, default: str|None = None):
        return cls(id, ParamKind.STRING, default=default)
    
    @classmethod
    def make_float(cls, id: str, min_value: float, max_value: float, default: float|None = None, slider: bool = True):
        return cls(id, ParamKind.FLOAT, min_value=min_value, max_value=max_value, default=default, slider=slider)
    
    def parse_str(self, value: str):
        if self.kind == ParamKind.ENUM or self.kind == ParamKind.STRING:
            return value
        elif self.kind == ParamKind.FLOAT:
            result = float(value)
            if self.min_value is not None:
                result = max(result, self.min_value)
            if self.max_value is not None:
                result = min(result, self.max_value)
            return result
        raise TypeError(f"Unknown parameter type '{self.kind}'")


class TranscodeContext(AsyncJobRuntimeContext):
    data: bytes
    params: Dict[str, Any]

    def __init__(self, base: AsyncJobRuntimeContext, data: bytes, params: Dict[str, Any]):
        self._extend(base)
        self.data = data
        self.params = params

    def set_progress(self, value: float):
        raise NotImplementedError()

ALL_TRANSCODERS: List["Transcoder"] = []


class Transcoder:
    input: Format
    output: Format
    params: List[ParamDef]
    _run: Callable[[TranscodeContext], bytes]
    _available: Callable[[], bool]|bool

    def __init__(self,
        input: Format, output: Format,
        params: List[ParamDef],
        run: Callable[[TranscodeContext], bytes],
        available: Callable[[], bool]|bool,
    ):
        self.input = input
        self.output = output
        self.params = params
        self._run = run
        self._available = available
        ALL_TRANSCODERS.append(self)

    def __repr__(self):
        return f"{self.input.mime} -> {self.output.mime}"
    
    def available(self):
        if isinstance(self._available, bool):
            return self._available
        return self._available()
    
    def run(self, context: TranscodeContext):
        return self._run(context)
    
    @classmethod
    def by_input(cls, input: Format):
        return [t for t in ALL_TRANSCODERS if t.input == input]
    
    @classmethod
    def find(cls, input: Format, output: Format):
        return next(t for t in ALL_TRANSCODERS if t.input == input and t.output == output)
