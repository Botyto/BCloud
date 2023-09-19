from asyncio import Event
from graphene import Argument, Field, ObjectType
import logging
from typing import Callable, Coroutine, Generic, List, Tuple, TypeVar
from uuid import UUID

from .types import TypesBuilder

from ...data.sql.database import Model

logger = logging.getLogger(__name__)


class SubscriptionBuilder:
    types: TypesBuilder

    def __init__(self, types: TypesBuilder)
        self.types = types

    def _collect(self):
        return []

    def _build_field(self, minfo: GqlMethodInfo):
        assert minfo.return_type is not None, "Subscriptions must return a value"
        assert not typeinfo.is_scalar(minfo.return_type), "Subscriptions must return a class"
        return_type = self.types.as_output(minfo.return_type)
        args = {}
        for name, type in minfo.param_types.items():
            gql_type = self.types.as_input(type)
            default = minfo.param_defaults.get(name, None)
            args[name] = Argument(
                gql_type,
                default_value=default,
            )
        return Field(return_type, description=minfo.method.__doc__, **args)

    def build(self):
        subscriptions = self._collect()
        if not subscriptions:
            logger.warn("No GraphQL subscriptions found")
        attrs = {}
        for method in subscriptions:
            minfo = GqlMethodInfo(self.types, method)
            name = minfo.get_binding_name()
            attrs[name] = self._build_field(minfo)
            attrs[f"subscribe_{name}"] = minfo.wrap()
        return type("Subscription", (ObjectType,), attrs)

ItemType = TypeVar("ItemType", bound=Model)
IdType = int|str|UUID
IdGetter = Callable[[ItemType], IdType]


class SubscriptionSync(Generic[ItemType]):
    _id_getter: IdGetter
    _capacity: int
    _buffer: List[Tuple[int, int|str]]
    _cursor: int
    _event: Event

    @staticmethod
    def default_id(item: ItemType) -> IdType:
        return item.id

    def __init__(self, id_getter: IdGetter = default_id, capacity: int = 5):
        self._id_getter = id_getter
        self._capacity = capacity
        self._buffer = []
        self._cursor = 0
        self._event = Event()

    def poll(self, cursor: int|None) -> Tuple[List[int|str]|None, int]:
        if not self._buffer:
            return None, self._cursor
        if cursor is None:
            cursor = self._buffer[0][0]
        if cursor == self._cursor:
            return None, self._cursor
        for i, (c, _) in enumerate(self._buffer):
            if c == cursor:
                return [pair[1] for pair in self._buffer[i:]], self._cursor

    def last(self) -> int|str|None:
        if self._buffer:
            return self._buffer[-1][1], self._cursor

    def push(self, item: ItemType):
        if len(self._buffer) == self._capacity:
            self._buffer.pop(0)
        item_id = self._id_getter(item)
        self._buffer.append((self._cursor, item_id))
        self._cursor += 1
        self._event.set()
        self._event.clear()

    def wait(self) -> Coroutine:
        return self._event.wait()
