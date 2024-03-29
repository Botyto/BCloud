from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.orm import class_mapper, object_session, InstrumentedAttribute, joinedload
from typing import Callable, Dict, List, Tuple, Type

from .data import User

from ..data.sql.database import Model

__all__ = [
    "owner_info",
    "resolve_owner_info",
    "traverse_chain",
]

def owner_info(**kwargs):
    return {
        "owner": True,
        **kwargs,
    }


@dataclass
class OwnerInfo:
    member: str
    optional: bool

NO_INFO = OwnerInfo("", False)

def find_owner_relationship(entity_type: Type[Model]) -> InstrumentedAttribute|None:
    relationships = class_mapper(entity_type).relationships
    for key, relationship in relationships.items():
        attr: InstrumentedAttribute = getattr(entity_type, key)
        attr_info = attr.info
        if attr_info is not None and attr_info.get("owner"):
            return attr
        
TYPE_OWNER_INFO: Dict[Type, OwnerInfo] = {}
def resolve_owner_info(entity_type: Type[Model]) -> OwnerInfo:
    owner_info = TYPE_OWNER_INFO.get(entity_type)
    if owner_info is None:
        attr = find_owner_relationship(entity_type)
        if attr is None:
            owner_info = NO_INFO
        else:
            optional = attr.info.get("optional", False)
            owner_info = OwnerInfo(attr.key, optional)
        TYPE_OWNER_INFO[entity_type] = owner_info
    return owner_info


@dataclass
class OwnerChainEntry:
    member: InstrumentedAttribute
    info: OwnerInfo

TYPE_OWNER_CHAIN: Dict[Type[Model], List[OwnerChainEntry]] = {}
def resolve_owner_chain(entity_type: Type[Model], entity_owner_info: OwnerInfo):
    owner_info: OwnerInfo|None = entity_owner_info
    chain = TYPE_OWNER_CHAIN.get(entity_type)
    if chain is None:
        chain = []
        current_cls = entity_type
        visited = set()
        while owner_info and owner_info is not NO_INFO:
            assert current_cls not in visited, f"Circular ownership for `{entity_type}`"
            visited.add(current_cls)
            member: InstrumentedAttribute = getattr(current_cls, owner_info.member)
            owner_class = member.prop.mapper.class_
            assert current_cls is not owner_class, f"Class `{current_cls}` cannot be its own owner"
            chain.append(OwnerChainEntry(member, owner_info))
            current_cls = owner_class
            owner_info = resolve_owner_info(owner_class)
        TYPE_OWNER_CHAIN[entity_type] = chain
    return chain

def traverse_chain(
    entity: Model,
    fn: Callable[[Model], None]|None,
) -> Tuple[User|None, OwnerInfo|None]:
    session = object_session(entity)
    assert session is not None, "Entity must be attached to a session"
    with session.no_autoflush:
        entity_type = type(entity)
        owner_info = resolve_owner_info(entity_type)
        if owner_info is NO_INFO:
            return None, None
        chain = resolve_owner_chain(entity_type, owner_info)
        joins = None
        for entry in chain:
            if joins is None:
                joins = joinedload(entry.member)
            else:
                joins = joins.joinedload(entry.member)
        statement = select(entity_type).options(joins)  # type: ignore
        for key in entity_type.__mapper__.primary_key:
            primary_key_attr = getattr(entity_type, key.name)
            primary_key_value = getattr(entity, key.name)
            statement = statement.where(primary_key_attr == primary_key_value)
        entity2 = session.scalars(statement).one()
        assert entity is entity2
        owner = entity
        info = None
        for entry in chain:
            info = entry.info
            if fn is not None:
                fn(owner)
            owner = getattr(owner, entry.member.key)
            if owner is None:
                break
        assert owner is None or isinstance(owner, User)
        return owner, info
