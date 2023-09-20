from types import MethodType
from typing import List, Type

from .types import TypesBuilder


class MethodBuilder:
    types: TypesBuilder
    methods: List[MethodType]

    def __init__(self, types: TypesBuilder, methods: List[MethodType]):
        self.types = types
        self.methods = methods

    def register(self, method: MethodType):
        self.methods.append(method)

    def build(self) -> Type:
        raise NotImplementedError()
