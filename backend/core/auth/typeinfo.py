import sqlalchemy
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.properties import RelationshipProperty
from typing import Any, cast, Type

from ..data.sql.database import Model
from ..data.sql.typeinfo import SqlTypeInfo, SqlTypeKind

from .owner import resolve_owner_info


class OwnedSqlTypeInfo(SqlTypeInfo):
    def _extract_class_info(self, obj_type: Any, **generic_args):
        super()._extract_class_info(obj_type, **generic_args)
        assert self.class_attrs is not None
        if not self.input:
            return
        attr_names = set(self.class_attrs)
        for name in attr_names:
            attr = self.class_attrs.get(name)
            if not isinstance(attr, RelationshipProperty):
                continue
            referenced_type = attr.mapper.class_
            referenced_owner_info = resolve_owner_info(referenced_type)
            if referenced_owner_info is None:
                continue
            referenced_owner_member = referenced_owner_info.member
            mapper: Mapper = sqlalchemy.inspect(referenced_type)
            referenced_owner_member = mapper.relationships[referenced_owner_member]
            if referenced_owner_member.mapper.class_ is not obj_type:
                del self.class_attrs[name]
                id_name = name + "_id"
                if id_name in attr_names:
                    del self.class_attrs[id_name]

    def postprocess_input(self, input):
        if self.kind == SqlTypeKind.CLASS:
            assert self.class_attrs is not None
            for name, attr in self.class_attrs.items():
                attr_input = getattr(input, name)
                if attr_input is None:
                    continue
                attr_type_info = OwnedSqlTypeInfo(attr, True)
                if not attr_type_info.is_class:
                    continue
                referenced_type = cast(Type[Model], attr_type_info.non_optional_type)
                referenced_owner_info = resolve_owner_info(referenced_type)
                if referenced_owner_info is None:
                    continue
                referenced_owner_member = referenced_owner_info.member
                if isinstance(attr_input, list):
                    for item in attr_input:
                        setattr(item, referenced_owner_member, input)
                else:
                    setattr(attr_input, referenced_owner_member, input)
        return input
