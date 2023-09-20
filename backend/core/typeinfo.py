from collections.abc import Generator, Iterable
from datetime import datetime, date, time, timedelta
from enum import Enum
import inspect
from types import NoneType, UnionType
from typing import Any, Callable, Dict, List, Optional, Protocol, Tuple, Type, TypeVar
from typing import _GenericAlias, _UnionGenericAlias
import typing
from uuid import UUID


SCALAR_TYPES_SET = {
    int, float, str, bool, bytes, dict, UUID,
    datetime, date, time, timedelta,
}

def is_scalar(obj_type: Type):
    return obj_type in SCALAR_TYPES_SET


class TypeInfoProtocol(Protocol):
    input: bool
    is_optional: bool
    is_list: bool
    is_union: bool
    is_enum: bool
    union_types: Type|None
    non_optional_type: Type|None
    is_generic: bool
    generic_args: Dict[str, Type]|None


class TypeInfo(TypeInfoProtocol):
    input: bool
    origin_type: Type
    is_optional: bool = False
    non_optional_type: Type|None = None
    union_types: Type|None = None
    is_list: bool = False
    generic_args: Dict[str, Type]|None = None
    is_enum: bool = False
    is_class: bool = False
    class_attrs: Dict[str, Type]|None = None
    resolved_attrs: Dict[str, Tuple[Type, Callable]]|None = None
    is_scalar: bool = False

    def __init__(self, obj_type: Any, input: bool, **generic_args):
        self.input = input
        self.origin_type = obj_type
        # strip optional type
        if isinstance(self.origin_type, _UnionGenericAlias) or isinstance(self.origin_type, UnionType):
            args = typing.get_args(self.origin_type)
            if NoneType in args:
                self.is_optional = True
                none_idx = args.index(NoneType)
                non_optional_types = args[:none_idx] + args[none_idx + 1:]
            else:
                non_optional_types = args
            if len(non_optional_types) > 1:
                self.union_types = non_optional_types
            else:
                self.non_optional_type = non_optional_types[0]
        elif isinstance(self.origin_type, _GenericAlias) and typing.get_origin(self.origin_type) is Optional:
            self.is_optional = True
            self.non_optional_type = typing.get_args(self.origin_type)[0]
        else:
            self.non_optional_type = self.origin_type
        # if there are many types - stop here and process the rest externally
        if self.union_types:
            return
        while True:
            last_type = self.non_optional_type
            if isinstance(self.non_optional_type, _GenericAlias):
                origin = typing.get_origin(self.non_optional_type)
                args = typing.get_args(self.non_optional_type)
                assert not origin is Dict, "Dictionaries cannot be represented in GraphQL"
                if origin in (Iterable, Generator, list, set, tuple):
                    self.is_list = True
                    self.non_optional_type = args[0]
                else:
                    self.generic_args = {
                        origin.__parameters__[i].__name__: arg
                        for i, arg in enumerate(args)
                    }
                    self.non_optional_type = origin
                    self.is_class = True
            elif inspect.isclass(self.non_optional_type):
                if issubclass(self.non_optional_type, Enum):
                    self.is_enum = True
                elif is_scalar(self.non_optional_type):
                    self.is_scalar = True
                else:
                    self.is_class = True
                    self.class_attrs = typing.get_type_hints(self.non_optional_type)
                    properties = inspect.getmembers(self.non_optional_type, lambda x: isinstance(x, property))
                    self.resolved_attrs = {}
                    for name, prop in properties:
                        if prop.fget:
                            return_type = typing.get_type_hints(prop.fget).get("return")
                            assert return_type, f"Property {name} of class {self.non_optional_type} has no return type"
                            self.resolved_attrs[name] = (return_type, prop.fget)
                    if hasattr(self.non_optional_type, "__parameters__") and not self.generic_args:
                        self.generic_args = {
                            param.__name__: generic_args.get(param.__name__)
                            for param in self.non_optional_type.__parameters__
                        }
            else:
                raise TypeError(f"Type '{self.non_optional_type}' is not supported in GraphQL")
            # Note: we don't support generics with multiple typevars
            if isinstance(self.non_optional_type, TypeVar):
                self.non_optional_type = generic_args[self.non_optional_type.__name__]
            elif self.non_optional_type is last_type:
                break

    @property
    def is_common(self):
        return self.is_enum or self.is_union

    @property
    def is_union(self):
        return not not self.union_types

    @property
    def is_generic(self):
        return not not self.generic_args

    def postprocess_input(self, input):
        return input


class MethodInfo:
    IGNORE_PARAMS = ("self", "_")

    method: Callable
    param_names: List[str]
    param_types: Dict[str, Type]
    param_defaults: Dict[str, Any]
    return_type: Type

    def __init__(self, method: Callable):
        self.method = method
        params = self.__extract_params()
        self.param_names = list(params)
        self.param_types = {name: p.annotation for name, p in params.items()}
        self.param_defaults = {name: p.default for name, p in params.items() if p.default is not inspect.Parameter.empty}
        self.return_type = typing.get_type_hints(method).get("return", None)

    @property
    def name(self):
        return self.method.__name__

    @property
    def package(self):
        method_module = inspect.getmodule(self.method)
        if method_module is not None:
            return method_module.__package__ or ""
        return ""

    @property
    def defining_class(self):
        method_module = inspect.getmodule(self.method)
        return getattr(method_module, self.method.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])

    @property
    def is_context_manager(self):
        return hasattr(self.defining_class, "__enter__") and hasattr(self.defining_class, "__exit__")

    @property
    def is_async_gen(self):
        return inspect.isasyncgenfunction(self.method)

    @property
    def is_async(self):
        return inspect.iscoroutinefunction(self.method) or self.is_async_gen
    
    def __extract_params(self):
        result: Dict[str, inspect.Parameter] = {}
        signature = inspect.signature(self.method)
        for name, param in signature.parameters.items():
            if name in self.IGNORE_PARAMS or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
                continue
            result[name] = param
        return result
