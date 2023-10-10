from datetime import datetime, timezone

from sqlalchemy import Column
from sqlalchemy import Boolean, Enum, Float, Integer, String, Text
from sqlalchemy import Date, DateTime, Interval, Time
from sqlalchemy import JSON, UUID, ForeignKey
from sqlalchemy.dialects.mysql import LONGBLOB as Bytes
from sqlalchemy.orm import InstrumentedAttribute, Mapped, mapped_column, relationship

STRING_MAX = 2**12 - 1

def utcnow_tz():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def strmaxlen(column_or_size: InstrumentedAttribute|int) -> int:
    if isinstance(column_or_size, int):
        return column_or_size
    assert isinstance(column_or_size, InstrumentedAttribute), "column_or_size must be a column or an int"
    column_type = column_or_size.type
    if isinstance(column_type, String):
        assert column_type.length is not None, "String column must have a length specified"
        return column_type.length
    elif isinstance(column_type, Text):
        return 2**32 - 1
    else:
        raise TypeError("Column is not a string-like column")

def ensure_str_fit(
        name: str,
        text: str,
        column_or_size: InstrumentedAttribute|int,
        accept_empty: bool = False,
        accept_none: bool = True,
        should_raise: bool = False
    ) -> str|bool:
    if text is None:
        if not accept_none:
            if not should_raise:
                return False
            raise TypeError(f"{name} is None")
        return text
    if not isinstance(text, str):
        if not should_raise:
            return False
        raise TypeError(f"{name} is not a string")
    if not accept_empty:
        if len(text) == 0:
            if not should_raise:
                return False
            raise ValueError(f"{name} is empty")
    maxlen = strmaxlen(column_or_size)
    if len(text) > maxlen:
        if not should_raise:
            return False
        raise ValueError(f"{name} is too long (max {maxlen} chars)")
    if not should_raise:
        return True
    return text

def fit_str(text: str, column: InstrumentedAttribute|int):
    maxlen = strmaxlen(column)
    if len(text) > maxlen:
        return text[:maxlen - 1] + "…"
    return text
