from enum import Enum as PyEnum
import logging
from sqlalchemy import event
from sqlalchemy.orm import class_mapper, Session, QueryContext, InstrumentedAttribute
from typing import Dict, Tuple, Type
from uuid import UUID

from .data import User
from .handlers import AuthError, AuthHandlerMixin
from .owner import OwnerInfo, traverse_chain

from ..data.sql.database import Model

logger = logging.getLogger(__name__)

__all__ = [
    "AccessLevel",
    "ensure_access",
    "will_read",
    "will_write",
]


class AccessLevel(PyEnum):
    SERVICE = "SERVICE"
    HIDDEN = "HIDDEN"
    SECURE = "SECURE"
    PRIVATE = "PRIVATE"
    PUBLIC_READABLE = "PUBLIC_READALBE"
    PUBLIC_WRITABLE = "PUBLIC_WRITABLE"

    @staticmethod
    def min():
        return ACCESS_ORDER[0]

    @staticmethod
    def max():
        return ACCESS_ORDER[-1]

    def __lt__(self, other):
        return ACCESS_ORDER.index(self) < ACCESS_ORDER.index(other)

    def __le__(self, other):
        return ACCESS_ORDER.index(self) <= ACCESS_ORDER.index(other)

    def __gt__(self, other):
        return ACCESS_ORDER.index(self) > ACCESS_ORDER.index(other)

    def __ge__(self, other):
        return ACCESS_ORDER.index(self) >= ACCESS_ORDER.index(other)

ACCESS_ORDER = [
    AccessLevel.SERVICE,
    AccessLevel.HIDDEN,
    AccessLevel.SECURE,
    AccessLevel.PRIVATE,
    AccessLevel.PUBLIC_READABLE,
    AccessLevel.PUBLIC_WRITABLE,
]


class AccessInfo:
    key: str

    def __init__(self, key: str):
        self.key = key

NO_INFO = AccessInfo("")
TYPE_ACCESS_INFO: Dict[Type, AccessInfo] = {}
def find_access_info(entity_type: Type[Model]) -> AccessInfo:
    access_info = TYPE_ACCESS_INFO.get(entity_type)
    if access_info is None:
        column_attrs = class_mapper(entity_type).column_attrs
        for column_attr in column_attrs:
            attr: InstrumentedAttribute = getattr(entity_type, column_attr.key)
            if attr.type.python_type == AccessLevel:
                if access_info is not None:
                    raise ValueError(f"Multiple access fields for entity type {entity_type}")
                attr_info = attr.info
                if attr_info is None:
                    access_info = AccessInfo(column_attr.key)
                    attr.info = {"access": access_info}  # type: ignore
                else:
                    access_info = attr.info.get("access")
        access_info = access_info or NO_INFO
        TYPE_ACCESS_INFO[entity_type] = access_info
    return access_info

def get_own_access_level(entity: Model) -> AccessLevel:
    access_info = find_access_info(type(entity))
    if access_info is not NO_INFO:
        return getattr(entity, access_info.key)
    else:
        implicit = AccessLevel.PRIVATE  # TODO implicit access
        if implicit is not None:
            return implicit
    return AccessLevel.PRIVATE

def get_access_level_and_owner(entity: Model) -> Tuple[AccessLevel, User|None, OwnerInfo|None]:
    max_access = AccessLevel.min()
    def update_access(entity):
        nonlocal max_access
        access = get_own_access_level(entity)
        if access > max_access:
            max_access = access
    owner, owner_info = traverse_chain(entity, update_access)
    return max_access, owner, owner_info

def ensure_access(user_id: UUID|None, target: Model, min_access: AccessLevel, should_raise: bool = True):
    access, owner, owner_info = get_access_level_and_owner(target)
    if owner is None:
        if owner_info is not None and not owner_info.optional:
            logger.warn("Owner is None for %s", target)
        return False
    assert isinstance(owner, User)
    if owner.id != user_id and access < min_access:
            if should_raise:
                raise AuthError("Item not owned by current user")
            else:
                return False
    return True

def will_read(user_id: UUID|None, target: Model, should_raise: bool = True):
    assert target is not None
    return ensure_access(user_id, target, AccessLevel.PUBLIC_READABLE, should_raise)

def will_write(user_id: UUID|None, target: Model, should_raise: bool = True):
    assert target is not None
    if user_id is None:
        raise AuthError("Not authenticated")
    return ensure_access(user_id, target, AccessLevel.PUBLIC_WRITABLE, should_raise)


class EnsureAccessContextManager:
    TAG = "ensuring_access"
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        count = self.session.info.get(self.TAG, 0)
        self.session.info[self.TAG] = count + 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.info[self.TAG] -= 1

def resolve_user_id(session: Session):
    handler = session.info.get("handler")
    if handler is None:
        return
    if not isinstance(handler, AuthHandlerMixin):
        return
    return handler.get_current_user()

@event.listens_for(Model, "load", propagate=True)
def on_instance_load(target: Model, context: QueryContext):
    session: Session = context.session
    if session.info.get(EnsureAccessContextManager.TAG, 0) > 0:
        return
    user_id = resolve_user_id(session)
    with EnsureAccessContextManager(session):
        will_read(user_id, target)

@event.listens_for(Session, "before_flush")
def on_before_flush(session: Session, flush_context, instances):
    if session.info.get(EnsureAccessContextManager.TAG, 0) > 0:
        return
    user_id = resolve_user_id(session)
    with EnsureAccessContextManager(session):
        for target in session.dirty:
            will_write(user_id, target)
