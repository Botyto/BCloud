from datetime import datetime, date, time, timedelta
from enum import Enum as PyEnum
import inspect
import sqlalchemy
from sqlalchemy import Column, Enum
from sqlalchemy.orm import Mapper, RelationshipProperty
from sqlalchemy.sql.sqltypes import UUID as SqlUUID
import sqlalchemy.dialects.mysql
from typing import Any, get_type_hints, List, Tuple, Type
from uuid import UUID

from .database import Model

from ...typeinfo import TypeInfo


class SqlTypeKind(PyEnum):
    CLASS = 1
    ATTR = 2

SQL_TO_SCALAR = {
    sqlalchemy.Integer: int,
    sqlalchemy.Float: float,
    sqlalchemy.Boolean: bool,
    sqlalchemy.String: str,
    sqlalchemy.Text: str,
    sqlalchemy.LargeBinary: bytes,
    sqlalchemy.dialects.mysql.LONGBLOB: bytes,
    sqlalchemy.JSON: dict,
    sqlalchemy.DateTime: datetime,
    sqlalchemy.TIMESTAMP: datetime,
    sqlalchemy.Date: date,
    sqlalchemy.Time: time,
    sqlalchemy.Interval: timedelta,
    SqlUUID: UUID,
}


class SqlTypeInfo(TypeInfo):
    kind: SqlTypeKind|None

    def __init__(self, obj_type: Any, input: bool, **generic_args):
        assert not generic_args, f"Generic arguments are not supported for SQL types"
        self.input = input
        self.origin_type = obj_type
        self.kind = self.get_sql_kind(obj_type)
        if self.kind == SqlTypeKind.CLASS:
            self._extract_class_info(obj_type, **generic_args)
        elif self.kind == SqlTypeKind.ATTR:
            if isinstance(obj_type, RelationshipProperty):
                self._extract_relationship_info(obj_type, **generic_args)
            else:
                self._extract_column_info(obj_type, **generic_args)
        else:
            raise TypeError(f"Unsupported SQL type {obj_type}")

    def _extract_class_info(self, obj_type: Type, **generic_args):
        mapper: Mapper = sqlalchemy.inspect(obj_type)
        self.non_optional_type = obj_type
        self.is_class = True
        columns = {col.key: col for col in mapper.columns}
        relationships = {rel.key: rel for rel in mapper.relationships}
        self.class_attrs = {**columns, **relationships}
        self.resolved_attrs = {}
        properties: List[Tuple[str, property]] = inspect.getmembers(self.non_optional_type, lambda x: isinstance(x, property))
        for name, prop in properties:
            if prop.fget:
                return_type = get_type_hints(prop.fget).get("return")
                assert return_type, f"Property {name} of class {self.non_optional_type} has no return type"
                self.resolved_attrs[name] = (return_type, prop.fget)
    
    def _extract_relationship_info(self, obj_type: RelationshipProperty, **generic_args):
        if obj_type.uselist:
            self.is_list = True
        self.is_optional = True  # TODO check if this is correct
        self.is_class = True
        self.non_optional_type = obj_type.mapper.class_
        mapper: Mapper = sqlalchemy.inspect(obj_type.mapper.class_)
        columns = {col.key: col for col in mapper.columns}
        relationships = {rel.key: rel for rel in mapper.relationships}
        self.class_attrs = {**columns, **relationships}

    def _extract_column_info(self, obj_type: Column, **generic_args):
        self.is_optional = obj_type.nullable != False
        sql_type = type(obj_type.type)
        scalar = SQL_TO_SCALAR.get(sql_type)  # type: ignore
        if scalar is not None:
            if scalar is int and obj_type.autoincrement and obj_type.primary_key:
                pass  # ID types aren't handled specially
            self.is_scalar = True
            self.non_optional_type = scalar
        elif sql_type is Enum:
            assert isinstance(obj_type.type, Enum)
            self.is_enum = True
            self.non_optional_type = obj_type.type.enum_class
        else:
            raise TypeError(f"Unsupported SQL type: {obj_type}")

    @staticmethod
    def get_sql_kind(obj_type: Any):
        if isinstance(obj_type, Type) and issubclass(obj_type, Model):
            return SqlTypeKind.CLASS
        elif isinstance(obj_type, (Column, RelationshipProperty)):
            return SqlTypeKind.ATTR

    def postprocess_input(self, input):
        if self.kind == SqlTypeKind.ATTR:
            if self.is_class and self.is_list and input is None:
                return []
        return super().postprocess_input(input)
