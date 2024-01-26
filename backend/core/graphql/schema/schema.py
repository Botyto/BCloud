from graphene import Schema

from .query import QueryBuilder
from .methods import MethodCollection
from .mutation import MutationBuilder
from .subscription import SubscriptionBuilder
from .types import TypesBuilder


class SchemaBuilder:
    types: TypesBuilder
    query: QueryBuilder
    mutation: MutationBuilder
    subscription: SubscriptionBuilder
    schema: Schema|None

    def __init__(self, methods: MethodCollection, package_prefix: str):
        self.types = TypesBuilder()
        self.query = QueryBuilder(self.types, methods.queries, package_prefix)
        self.mutation = MutationBuilder(self.types, methods.mutations, package_prefix)
        self.subscription = SubscriptionBuilder(self.types, methods.subscriptions, package_prefix)
        self.schema = None

    def build(self):
        if self.schema is None:
            query_cls = self.query.build()
            mutation_cls = self.mutation.build()
            subscription_cls = self.subscription.build()
            self.types.finish()
            self.schema = Schema(
                query=query_cls,
                mutation=mutation_cls,
                subscription=subscription_cls,
                types=self.types.all_types.values(),
                auto_camelcase=True,
            )
        return self.schema
