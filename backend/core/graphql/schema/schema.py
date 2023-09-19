from graphene import Schema

from .query import QueryBuilder
from .mutation import MutationBuilder
from .subscription import SubscriptionBuilder
from .types import TypesBuilder


class SchemaBuilder:
    types: TypesBuilder
    query: QueryBuilder
    mutation: MutationBuilder
    subscription: SubscriptionBuilder

    def __init__(self):
        self.types = TypesBuilder()
        self.query = QueryBuilder(self.types)
        self.mutation = MutationBuilder(self.types)
        self.subscription = SubscriptionBuilder(self.types)

    def build(self):
        query_cls = self.query.build()
        mutation_cls = self.mutation.build()
        subscription_cls = self.subscription.build()
        return Schema(
            query=query_cls,
            mutation=mutation_cls,
            subscription=subscription_cls,
            types=self.types.all_types.values(),
            auto_camelcase=True,
        )
