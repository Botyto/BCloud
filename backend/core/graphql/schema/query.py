from graphene import Argument, Field, ObjectType
import logging

from .builder import MethodBuilder

from ..typeinfo import GqlMethodInfo
from ...typeinfo import is_scalar

logger = logging.getLogger(__name__)


class QueryBuilder(MethodBuilder):
    def _build_field(self, minfo: GqlMethodInfo):
        assert minfo.return_type is not None, "Queries must return a value"
        assert not is_scalar(minfo.return_type), "Queries must return a class"
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
        if not self.methods:
            logger.warn("No GraphQL queries found")
            return
        query_attrs = {}
        for chain in self._method_chains():
            minfo = chain.method_info
            name = chain.binding_name
            query_attrs[name] = self._build_field(minfo)
            query_attrs[f"resolve_{name}"] = minfo.wrap()
        return type("Query", (ObjectType,), query_attrs)
