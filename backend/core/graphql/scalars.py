from datetime import timedelta
from graphene import Scalar
from graphql import GraphQLError
from graphql.language import StringValueNode, print_ast
import json
import re
from uuid import UUID as PyUUID


class Json(Scalar):
    """The `Json` scalar type represents a JSON value"""

    @staticmethod
    def serialize(obj):
        if not isinstance(obj, (dict)):
            raise GraphQLError(f"Json cannot represent value: {repr(obj)}")
        return json.dumps(obj)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(f"Json cannot represent non-string value: {print_ast(node)}")
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, dict):
            return value
        if not isinstance(value, str):
            raise GraphQLError(f"Json cannot represent non-string value: {repr(value)}")
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            raise GraphQLError(f"Json cannot represent value: {repr(value)}")


class Timedelta(Scalar):
    """The `timedelta` scalar type represents a duration value"""

    @staticmethod
    def serialize(obj):
        if not isinstance(obj, (timedelta)):
            raise GraphQLError(f"Timedelta cannot represent value: {repr(obj)}")
        return f"{obj.days}D{obj.seconds}S{obj.microseconds}US"

    PATTERN = re.compile(r"(\d+)D(\d+)S(\d+)US")
    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(f"Timedelta cannot represent non-string value: {print_ast(node)}")
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, timedelta):
            return value
        if not isinstance(value, str):
            raise GraphQLError(f"Timedelta cannot represent non-string value: {repr(value)}")
        match = Timedelta.PATTERN.match(value)
        if match:
            return timedelta(
                days=int(match.group(1)),
                seconds=int(match.group(2)),
                microseconds=int(match.group(3)),
            )
        else:
            raise GraphQLError(f"Timedelta cannot represent value: {repr(value)}")


class UUID(Scalar):
    """The `UUID` scalar type represents a UUID value"""

    @staticmethod
    def serialize(obj):
        if not isinstance(obj, (PyUUID)):
            raise GraphQLError(f"UUID cannot represent value: {repr(obj)}")
        return str(obj)

    @classmethod
    def parse_literal(cls, node, _variables=None):
        if not isinstance(node, StringValueNode):
            raise GraphQLError(f"UUID cannot represent non-string value: {print_ast(node)}")
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        if isinstance(value, PyUUID):
            return value
        if not isinstance(value, str):
            raise GraphQLError(f"UUID cannot represent non-string value: {repr(value)}")
        try:
            return PyUUID(value)
        except ValueError:
            raise GraphQLError(f"UUID cannot represent value: {repr(value)}")
