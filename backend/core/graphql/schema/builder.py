from dataclasses import dataclass
import inspect
import itertools
import sys
from types import MethodType, ModuleType
from typing import List, Type

from .types import TypesBuilder

from ..typeinfo import GqlMethodInfo


@dataclass
class ClassNode:
    class_type: Type
    method_infos: List[GqlMethodInfo]


@dataclass
class PackageNode:
    module: ModuleType
    classes: List[ClassNode]


class MethodBuilder:
    types: TypesBuilder
    methods: List[MethodType]
    package_prefix: str

    def __init__(self, types: TypesBuilder, methods: List[MethodType], package_prefix: str):
        self.types = types
        self.methods = methods
        self.package_prefix = package_prefix

    def register(self, method: MethodType):
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
        infos = [GqlMethodInfo(self.types, m) for m in self.methods]
        by_class = itertools.groupby(infos, lambda i: i.defining_class)
        classes = [ClassNode(class_type, list(methods)) for class_type, methods in by_class]
        by_module = itertools.groupby(classes, lambda c: self._find_package(c.class_type))
        return [PackageNode(module, list(classes)) for module, classes in by_module]

    def build(self) -> Type:
        raise NotImplementedError()
