from datetime import datetime, date, time, timedelta
import graphene
from graphql import GraphQLResolveInfo
import inspect
from typing import Any, Callable, TYPE_CHECKING

from .context import GraphQLContext
from .scalars import GrapheneJson, GrapheneTimedelta
if TYPE_CHECKING:
    from .schema.types import TypesBuilder

from ..auth.typeinfo import OwnedSqlTypeInfo
from ..typeinfo import SCALAR_TYPES_SET, TypeInfoProtocol, TypeInfo, MethodInfo

SCALAR_TYPES_TO_GQL = {
    int: graphene.Int,
    float: graphene.Float,
    str: graphene.String,
    bool: graphene.Boolean,
    datetime: graphene.DateTime,
    date: graphene.Date,
    time: graphene.Time,
    timedelta: GrapheneTimedelta,
    bytes: graphene.String,
    dict: GrapheneJson,
}
assert SCALAR_TYPES_SET == set(SCALAR_TYPES_TO_GQL)

def cap(s: str):
    return s[0].upper() + s[1:]


class GqlTypeNameMixin:
    @property
    def name(self: TypeInfoProtocol):
        result = ""
        if self.input:
            result += "Input"
        if self.is_optional:
            result += "Null"
        if self.is_list:
            result += "List"
        elif self.is_union:
            result += "Union"
        elif self.is_enum:
            result += "Enum"
        if self.is_union:
            assert self.union_types is not None
            result += "".join(GqlTypeInfo(t, False).name for t in self.union_types)
        else:
            assert self.non_optional_type is not None
            # result += "".join(cap(part) for part in re.split(r"[\._]", self.non_optional_type.__module__))
            non_opt_name: str = self.non_optional_type.__name__
            result += "".join(cap(part) for part in non_opt_name.split("_"))
            if self.is_generic:
                assert self.generic_args is not None
                result += "".join(GqlTypeInfo(t, False).name for t in self.generic_args.values())
        return result


class GqlTypeInfo(GqlTypeNameMixin, TypeInfo):
    pass


class GqlSqlTypeInfo(GqlTypeNameMixin, OwnedSqlTypeInfo):
    pass


class GqlMethodInfo(MethodInfo):
    builder: "TypesBuilder"

    def __init__(self, builder: "TypesBuilder", method: Callable):
        super().__init__(method)
        self.builder = builder

    def get_binding_name(self):
        def cap(s: str):
            return s[0].upper() + s[1:]
        def decap(s: str):
            return s[0].lower() + s[1:]

        prefix = None  # TODO extract from defining class
        if prefix is None:
            prefix = self.package.split('.')[-1]
        prefix = "".join(cap(part) for part in prefix.split("_"))
        name = "".join(cap(part) for part in self.method.__name__.split("_"))
        return decap(prefix + name)

    def wrap(self):
        method = self.method
        defining_class = self.defining_class
        builder = self.builder
        param_types = self.param_types
        signature = inspect.signature(defining_class)
        params = list(signature.parameters.values())
        assert len(params) == 2, f"Method {method} must have only 2 parameters: root, info"
        assert params[0].name == "handler", f"Method {method} has no handler parameter"
        assert params[1].name == "context", f"Method {method} has no context parameter"
        def convert_input(param: str, value: Any):
            expected_type = param_types.get(param)
            return builder.convert_input(value, expected_type)
        def convert_kwargs(**kwargs):
            return {k: convert_input(k, v) for k, v in kwargs.items()}
        
        if not self.is_async:
            if self.is_context_manager:
                def wrapper_sync_ctx(root, info: GraphQLResolveInfo, **kwargs):
                    context = GraphQLContext(info.context, info)
                    kwargs = convert_kwargs(**kwargs)
                    with defining_class(root, context) as obj:
                        return method(obj, **kwargs)
                return wrapper_sync_ctx
            else:
                def wrapper_sync(root, info: GraphQLResolveInfo, **kwargs):
                    context = GraphQLContext(info.context, info)
                    kwargs = convert_kwargs(**kwargs)
                    obj = defining_class(root, context)
                    return method(obj, **kwargs)
                return wrapper_sync
        else:
            if self.is_context_manager:
                raise NotImplementedError()
            if self.is_async_gen:
                async def wrapper_async_gen(root, info: GraphQLResolveInfo, **kwargs):
                    context = GraphQLContext(info.context, info)
                    kwargs = convert_kwargs(**kwargs)
                    obj = defining_class(root, context)
                    generator = method(obj, **kwargs)
                    async for value in generator:
                        yield value
                return wrapper_async_gen
            else:
                async def wrapper_async(root, info: GraphQLResolveInfo, **kwargs):
                    context = GraphQLContext(info.context, info)
                    kwargs = convert_kwargs(**kwargs)
                    obj = defining_class(root, context)
                    return await method(obj, **kwargs)
                return wrapper_async
        raise TypeError("This type of resolver is not supported")
