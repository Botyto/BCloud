from abc import ABC, abstractmethod
from dataclasses import dataclass
import inspect
import itertools
import sys
from types import ModuleType
from typing import Callable, List, Type

from .methods import MethodBuildInfo, WrapMethodType
from .types import TypesBuilder

from ..typeinfo import GqlMethodInfo


class GqlMethodInfoWithWrap(GqlMethodInfo):
    wrap_method: WrapMethodType

    def __init__(self, wrap_method: WrapMethodType, builder: TypesBuilder, method: Callable):
        super().__init__(builder, method)
        self.wrap_method = wrap_method


@dataclass
class ClassNode:
    class_type: Type
    method_infos: List[GqlMethodInfoWithWrap]


@dataclass
class PackageNode:
    module: ModuleType
    classes: List[ClassNode]


@dataclass
class MethodChain:
    method_info: GqlMethodInfoWithWrap
    class_type: Type
    package: ModuleType

    @property
    def binding_name(self):
        return self._to_gql_name(
            self.package.__name__.split(".")[-1],
            self.class_type.__name__,
            self.method_info.method.__name__,
        )

    @classmethod
    def _to_gql_name(cls, *parts: str):
        def cap(s: str):
            return s[0].upper() + s[1:]
        def decap(s: str):
            return s[0].lower() + s[1:]
        split_parts = [p for whole in parts for p in whole.split("_")]
        split_parts = [p for whole in split_parts for p in whole.split(".")]
        split_parts = [p.lower() for p in split_parts]
        split_parts = [p.replace("module", "") for p in split_parts]
        return decap("".join(cap(part) for part in split_parts))
    
    def wrap(self):
        return self.method_info.wrap_method(self.method_info)



class MethodBuilder(ABC):
    types: TypesBuilder
    methods: List[MethodBuildInfo]
    package_prefix: str

    def __init__(self, types: TypesBuilder, methods: List[MethodBuildInfo], package_prefix: str):
        self.types = types
        self.methods = methods
        self.package_prefix = package_prefix

    def register(self, method: MethodBuildInfo):
        self.methods.append(method)

    def _find_package(self, class_type: Type) -> ModuleType:
        module = inspect.getmodule(class_type)
        assert module is not None, "Class must be defined in a module"
        assert module.__package__ is not None, "Module must be in a package"
        module = sys.modules.get(module.__package__)
        assert module is not None, "Package must be loaded"
        path = module.__name__
        if self.package_prefix and path != self.package_prefix:
            if path.startswith(self.package_prefix):
                period_idx = path.find(".", len(self.package_prefix) + 1)
                if period_idx >= 0:
                    path = path[:period_idx]
                    module = sys.modules[path]
            else:
                pass  # class not in expected prefix - use the class package
        return module

    def _structured_methods(self) -> List[PackageNode]:
        infos = [GqlMethodInfoWithWrap(m.wrap, self.types, m.method) for m in self.methods]
        by_class = itertools.groupby(infos, lambda i: i.defining_class)
        classes = [ClassNode(class_type, list(methods)) for class_type, methods in by_class]
        by_module = itertools.groupby(classes, lambda c: self._find_package(c.class_type))
        return [PackageNode(module, list(classes)) for module, classes in by_module]
    
    def _method_chains(self) -> List[MethodChain]:
        chains = []
        for package in self._structured_methods():
            for class_node in package.classes:
                for method_info in class_node.method_infos:
                    chains.append(MethodChain(method_info, class_node.class_type, package.module))
        return chains
    
    @abstractmethod
    def build(self) -> Type:
        ...
