import graphene
import types
import typing


class InProgressException(Exception):
    pass


class DelayedType:
    obj_type: typing.Type
    cache: typing.Dict
    input: bool
    generic_args: typing.Dict[str, typing.Type]

    def __init__(self, obj_type: typing.Type, cache: typing.Dict, input: bool, **generic_args):
        self.obj_type = obj_type
        self.cache = cache
        self.input = input
        self.generic_args = generic_args

    def resolve(self, builder: "TypesBuilder"):
        return builder._construct_gql_type(self.obj_type, self.cache, self.input, **self.generic_args)

in_progress_marker = object()


class TypesBuilder:
    tinfos: typing.Dict[int, typeinfo.GqlTypeInfo] = {}
    all_types: typing.Dict[int, typing.Type[graphene.ObjectType]|typing.Type[graphene.InputObjectType]] = {}
    common_types: typing.Dict[int, typing.Type[graphene.ObjectType]|typing.Type[graphene.InputObjectType]] = {}
    ouput_types: typing.Dict[int, typing.Type[graphene.ObjectType]] = {}
    input_types: typing.Dict[int, typing.Type[graphene.InputObjectType]] = {}
    any_delayed: bool = False
    finished: bool = False

    def _typekey(self, obj_type: typing.Type, input: bool, **generic_args):
        if generic_args:
            return hash((obj_type, input, *sorted(generic_args.items())))
        else:
            return hash((obj_type, input))

    def typeinfo(self, obj_type: typing.Type, input: bool, **generic_args):
        type_key = self._typekey(obj_type, input, **generic_args)
        result = self.tinfos.get(type_key)
        if result is None:
            if typeinfo.GqlSqlTypeInfo.get_sql_kind(obj_type):
                result = typeinfo.GqlSqlTypeInfo(obj_type, input, **generic_args) 
            else:
                result = typeinfo.GqlTypeInfo(obj_type, input, **generic_args)
            self.tinfos[type_key] = result
        return result

    def gqlname(self, obj_type: typing.Type, input: bool, **generic_args):
        return self.typeinfo(obj_type, input, **generic_args).name

    def as_output(self, obj_type: typing.Type):
        return self._construct_gql_type(obj_type, self.ouput_types, False)

    def as_input(self, obj_type: typing.Type):
        return self._construct_gql_type(obj_type, self.input_types, True)
    
    def _construct_gql_type(self, obj_type: typing.Type, cache: typing.Dict, input: bool, **generic_args):
        assert not self.finished, "GraphQL type binding has been finished already"
        result = None
        tinfo = self.typeinfo(obj_type, input, **generic_args)
        non_optional_type = tinfo.non_optional_type
        assert not input or not tinfo.is_union, "Unions cannot be used as input types"
        try:
            if tinfo.is_scalar:
                result = self._construct_gql_scalar(non_optional_type)
            elif tinfo.is_enum:
                result = self._construct_gql_enum(non_optional_type, input)
            elif tinfo.is_union:
                result = self._construct_gql_union(obj_type, cache, input)
            elif tinfo.is_class:
                result = self._construct_gql_class(non_optional_type, cache, input, **(tinfo.generic_args or {}))
        except InProgressException:
            return DelayedType(obj_type, cache, input, **generic_args)

        assert result, f"Cannot construct GraphQL type for {non_optional_type}"
        if tinfo.is_list:
            result = graphene.List(result)
        if not tinfo.is_optional:
            result = graphene.NonNull(result)
        return result

    def _construct_gql_enum(self, obj_type: typing.Type, input: bool):
        type_key = self._typekey(obj_type, input)
        result = self.common_types.get(type_key)
        if result is in_progress_marker:
            self.any_delayed = True
            raise InProgressException()
        elif not result:
            self.common_types[type_key] = in_progress_marker
            binding_name = self.gqlname(obj_type, input)
            result = graphene.Enum.from_enum(obj_type, description=obj_type.__doc__, name=binding_name)
            self._cache_binding(self.common_types, obj_type, result, input)
        return result

    def _construct_gql_union(self, obj_type: typing.Type, cache: typing.Dict, input: bool):
        type_key = self._typekey(obj_type, input)
        result = self.common_types.get(type_key)
        if result is in_progress_marker:
            self.any_delayed = True
            raise InProgressException()
        elif not result:
            self.common_types[type_key] = in_progress_marker
            tinfo = self.typeinfo(obj_type, input)
            binding_name = self.gqlname(obj_type, input)
            assert not any(self._construct_gql_scalar(t) for t in tinfo.union_types), "Unions cannot contain scalar types"
            item_types = [self._construct_gql_type(t, cache, input) for t in tinfo.union_types]
            atts = {
                "Meta": type("Meta", (), {
                    "name": binding_name,
                    "types": item_types,
                }),
            }
            result = type(binding_name, (graphene.Union,), atts)
            self._cache_binding(self.common_types, obj_type, result, input)
        return result

    def _construct_gql_class(self, obj_type: typing.Type, cache: typing.Dict, input: bool, **generic_args):
        type_key = self._typekey(obj_type, input, **generic_args)
        result = cache.get(type_key)
        if result is in_progress_marker:
            self.any_delayed = True
            raise InProgressException()
        elif not result:
            cache[type_key] = in_progress_marker
            ignored_fields = None  # TODO get ignored fields for type
            tinfo = self.typeinfo(obj_type, input)
            binding_name = self.gqlname(obj_type, input, **generic_args)
            class_attrs = {}
            for attr_name, attr_type in tinfo.class_attrs.items():
                if ignored_fields is not None and attr_name in ignored_fields:
                    continue
                field_type = self._construct_gql_type(attr_type, cache, input, **generic_args)
                class_attrs[attr_name] = graphene.Field(field_type)
            if not input and tinfo.resolved_attrs is not None:
                for resolved_name, resolved_info in tinfo.resolved_attrs.items():
                    if ignored_fields and resolved_name in ignored_fields:
                        continue
                    resolved_type, resolver_func = resolved_info
                    field_type = self._construct_gql_type(resolved_type, cache, input, **generic_args)
                    class_attrs[resolved_name] = graphene.Field(field_type)
                    # see https://stackoverflow.com/questions/3431676/creating-functions-in-a-loop
                    def generate_resolver(resolver_func):
                        def wrapped_resolver(self, _: graphene.ResolveInfo):
                            return resolver_func(self)
                        return wrapped_resolver
                    class_attrs["resolve_" + resolved_name] = generate_resolver(resolver_func)
            class_attrs["Meta"] = type("Meta", (), {
                "name": binding_name,
                "description": obj_type.__doc__,
            })
            parent_type = graphene.InputObjectType if input else graphene.ObjectType
            result = type(binding_name, (parent_type,), class_attrs)
            self._cache_binding(cache, obj_type, result, input, **generic_args)
        return result

    def _construct_gql_scalar(self, obj_type: typing.Type):
        assert obj_type is not types.NoneType, "NoneType cannot be represented in GraphQL"
        return typeinfo.scalar_types_to_gql.get(obj_type)

    def _cache_binding(self, cache: typing.Dict, obj_type: typing.Type, gql_type: typing.Type, input: bool, **generic_args):
        type_key = self._typekey(obj_type, input, **generic_args)
        assert type_key not in cache or cache[type_key] == in_progress_marker, f"GraphQL type for {obj_type} has already been cached"
        cache[type_key] = gql_type
        self.all_types[type_key] = gql_type

    def finish(self):
        while self.any_delayed:
            self.any_delayed = False
            for type in self.all_types.values():
                if issubclass(type, graphene.Union):
                    for i in range(len(type._meta.types)):
                        type_i = type._meta.types[i]
                        if isinstance(type_i, DelayedType):
                            type._meta.types[i] = type_i.resolve(self)
                elif issubclass(type, (graphene.ObjectType, graphene.InputObjectType)):
                    for attr_name, attr in type.__dict__.items():
                        if isinstance(attr, graphene.Field):
                            if isinstance(attr.type, DelayedType):
                                attr._type = attr.type.resolve(self)
        self.finished = True

    def convert_input(self, input_value: typing.Any, expected_type: typing.Type):
        assert self.finished, "GraphQL type binding has to be finished before input conversion"
        return self._convert_input_obj(input_value, expected_type)

    def _convert_input_obj(self, input_value: typing.Any, expected_type: typing.Type):
        if expected_type is types.NoneType:
            assert input_value is None
            return None
        if input_value is None:
            return None
        expected_tinfo = self.typeinfo(expected_type, True)
        expected_tkey = self._typekey(expected_tinfo.non_optional_type, True)
        gql_type = self.all_types.get(expected_tkey)
        if expected_tinfo.is_list:
            return [self._convert_input_obj(v, expected_tinfo.non_optional_type) for v in input_value]
        if typeinfo.is_scalar(expected_tinfo.non_optional_type):
            return self._convert_input_scalar(input_value, expected_tinfo.non_optional_type)
        elif isinstance(gql_type, typing.Type):
            if issubclass(gql_type, graphene.InputObjectType):
                return self._convert_input_class(input_value, expected_type)
            elif issubclass(gql_type, graphene.Enum):
                return self._convert_input_enum(input_value, expected_type)
            elif issubclass(gql_type, graphene.Union):
                return self._convert_input_union(input_value, expected_type)    
        raise ValueError(f"Cannot convert input value {input_value}")

    def _convert_input_class(self, input_value: graphene.InputObjectType, expected_type: typing.Type):
        native_value = expected_type()
        expected_tinfo = self.typeinfo(expected_type, True)
        for field_name in input_value._meta.fields.keys():
            expected_attr_type = expected_tinfo.class_attrs[field_name]
            expected_attr_tinfo = self.typeinfo(expected_attr_type, True)
            gql_attr_value = getattr(input_value, field_name)
            native_attr_value = self._convert_input_obj(gql_attr_value, expected_attr_type)
            native_attr_value = expected_attr_tinfo.postprocess_input(native_attr_value)
            setattr(native_value, field_name, native_attr_value)
        native_value = expected_tinfo.postprocess_input(native_value)
        return native_value

    def _convert_input_enum(self, input_value: typing.Any, expected_type: typing.Type):
        expected_tinfo = self.typeinfo(expected_type, True)
        native_enum_type = expected_tinfo.non_optional_type
        native_enum_value = native_enum_type(input_value)
        native_enum_value = expected_tinfo.postprocess_input(native_enum_value)
        return native_enum_value

    def _convert_input_union(self, input_value: typing.Any, expected_type: typing.Type):
        raise ValueError(f"GraphQL doesn't support unions as input types")

    def _convert_input_scalar(self, input_value: typing.Any, expected_type: typing.Type):
        if not isinstance(input_value, expected_type):
            raise ValueError(f"Cannot convert input type {type(input_value)} to {expected_type}")
        return input_value
