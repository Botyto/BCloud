from sqlalchemy import select
from sqlalchemy.orm import MappedColumn, object_session
from typing import Callable, Dict, List, Tuple, Type

from .data import User

from ..data.sql.database import Model


class OwnerInfo:
    member: str
    optional: bool

    def __init__(self, member: str, optional: bool):
        self.member = member
        self.optional = optional

TYPE_OWNER_INFO: Dict[Type, OwnerInfo] = {}
TYPE_OWNER_CHAIN: Dict[Type[Model], List[Tuple[MappedColumn, OwnerInfo]]] = {}
def traverse_ownership_chain(
    entity: Model,
    fn: Callable[[Model], None]|None,
) -> Tuple[User|None, OwnerInfo|None]:
    session = object_session(entity)
    assert session is not None, "Entity must be attached to a session"
    entity_class = type(entity)
    owner_info = TYPE_OWNER_INFO.get(entity_class)
    if owner_info is None:
        return None, None
    chain = TYPE_OWNER_CHAIN.get(entity_class)
    if chain is None:
        chain = []
        current_cls = entity_class
        visited = set()
        while owner_info:
            # TODO make this check static
            if current_cls in visited:
                raise RuntimeError(f"Ownership chain for {entity_class} is circular")
            visited.add(current_cls)
            member: MappedColumn = getattr(current_cls, owner_info.member)
            owner_class = member.column.type.python_type
            assert current_cls is not owner_class, f"Class {current_cls} cannot be its own owner"
            chain.append((member, owner_info))
            current_cls = owner_class
            owner_info = TYPE_OWNER_INFO.get(owner_class)
        TYPE_OWNER_CHAIN[entity_class] = chain
    statement = select(entity_class)
    for member, _ in chain:
        statement = statement.join(member).add_columns(member.column.type.python_type)
    for key in entity_class.__mapper__.primary_key:
        primary_key_attr = getattr(entity_class, key.name)
        primary_key_value = getattr(entity, key.name)
        statement = statement.filter(primary_key_attr == primary_key_value)
    entity2 = session.scalars(statement).one()
    assert entity is entity2
    assert isinstance(entity, User)
    owner = entity
    for member, info in chain:
        if fn is not None:
            fn(owner)
        owner = getattr(owner, member.column.key)
        if owner is None:
            break
    return owner, info
