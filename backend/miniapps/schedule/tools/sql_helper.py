from typing import Iterable

from sqlalchemy.orm import object_session, class_mapper, make_transient, RelationshipProperty

from core.data.sql.columns import String, ensure_str_fit
from core.data.sql.database import Model
from core.auth.owner import resolve_owner_info

# TODO move function to a common, easily accessible place
# Note that it cannot be in core.data.sql, becuase of the core.auth.owner (circular) import
def copy_columns(src: Model, dst: Model, exclude: Iterable[str]|None = None):
    assert exclude is None or "id" not in exclude, "`id` is excluded from copying by default"
    if type(src) != type(dst):
        raise TypeError(f"Cannot copy {type(src)} object onto {type(dst)}")
    src_session = object_session(src)
    if src_session is not None:
        raise ValueError("Cannot copy from object with a session")
    dst_session = object_session(dst)
    if dst_session is None:
        raise ValueError("Cannot copy to object without a session")
    # columns to ignore
    exclude_set = set(exclude) if exclude else set()
    exclude_set.add("id")
    owner_info = resolve_owner_info(dst.__class__)
    if owner_info is not None:
        exclude_set.add(owner_info.member)
        for column in dst.__mapper__.relationships[owner_info.member].local_columns:
            exclude_set.add(column.name)
    mapper = class_mapper(type(dst))
    # copy columns
    for column in mapper.columns:
        if column.name in exclude_set:
            continue
        # check if column is string and it fits
        if isinstance(column.type, String) and column.type.length is not None:
            # TODO implement for Text props - see core.data.sql.columns.strmaxlen
            dst_value = getattr(dst, column.name)
            ensure_str_fit(column.name, dst_value, column.type.length, accept_empty=True, accept_none=not not column.nullable)
        setattr(dst, column.name, getattr(src, column.name))
    # copy relationships
    def remap_child(relationship: RelationshipProperty, child: Model):
        if relationship.back_populates is not None:
            setattr(child, relationship.back_populates, dst)
        if relationship.local_remote_pairs is not None:
            for local_column, remote_column in relationship.local_remote_pairs:
                setattr(child, remote_column.name, getattr(dst, local_column.name))
        dst_session.add(child)
    for relationship in mapper.relationships:
        if relationship.key in exclude_set:
            continue
        if relationship.uselist:
            src_children = getattr(src, relationship.key)
            dst_children = getattr(dst, relationship.key)
            for child in dst_children:
                dst_session.delete(child)
            for child in list(src_children):
                remap_child(relationship, child)
        else:
            src_child = getattr(src, relationship.key)
            dst_child = getattr(dst, relationship.key)
            make_transient(src_child)
            copy_columns(src_child, dst_child)
            remap_child(relationship, src_child)
    assert object_session(src) is None, "Source object changed session"
