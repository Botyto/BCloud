from graphene import Argument, Mutation, ObjectType
import logging

from .builder import MethodBuilder, MethodChain

logger = logging.getLogger(__name__)

def cap(s: str):
    return s[0].upper() + s[1:]


class MutationBuilder(MethodBuilder):
    def _build_class(self, chain: MethodChain, name: str):
        input_attrs = {}
        minfo = chain.method_info
        for name, param_type in minfo.param_types.items():
            gql_type = self.types.as_input(param_type)
            default = minfo.param_defaults.get(name, None)
            input_attrs[name] = Argument(
                gql_type,
                default_value=default,
            )
        input_cls = type("Arguments", (), input_attrs)

        mutation_attrs = {
            "Arguments": input_cls,
            "mutate": chain.wrap(),
        }
        assert minfo.return_type is not None, f"Mutation {minfo.method} must return a value"
        return_type_info = self.types.typeinfo(minfo.return_type, False)
        assert return_type_info.is_class, f"Mutation {minfo.method} must return a class"
        mutation_attrs["Output"] = self.types.as_output(minfo.return_type)
        
        mutation_attrs["description"] = minfo.method.__doc__

        mutation_cls_name = f"{name}_mutation"
        mutation_cls_name = "".join(cap(part) for part in mutation_cls_name.split("_"))
        return type(mutation_cls_name, (Mutation,), mutation_attrs)

    def build(self):
        if not self.methods:
            logger.warn("No GraphQL mutations found")
            return
        mutation_attrs = {}
        for chain in self._method_chains():
            name = chain.binding_name
            mutation_cls = self._build_class(chain, name)
            mutation_attrs[name] = mutation_cls.Field()
        return type("Mutation", (ObjectType,), mutation_attrs)
