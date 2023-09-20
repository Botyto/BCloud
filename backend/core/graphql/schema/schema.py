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

    def __init__(self, methods: MethodCollection):
        self.types = TypesBuilder()
        self.query = QueryBuilder(self.types, methods.queries)
        self.mutation = MutationBuilder(self.types, methods.mutations)
        self.subscription = SubscriptionBuilder(self.types, methods.subscriptions)

    def build(self):
        query_cls = self.query.build()
        mutation_cls = self.mutation.build()
        subscription_cls = self.subscription.build()
        self.types.finish()
        return Schema(
            query=query_cls,
            mutation=mutation_cls,
            subscription=subscription_cls,
            types=self.types.all_types.values(),
            auto_camelcase=True,
        )
