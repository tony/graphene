from functools import partial
import six
from graphql_relay import mutation_with_client_mutation_id

from ..types.mutation import Mutation, MutationMeta
from ..types.inputobjecttype import InputObjectType
from ..types.field import Field, InputField
from ..utils.get_fields import get_fields
from ..utils.copy_fields import copy_fields
from ..utils.props import props


class ClientIDMutationMeta(MutationMeta):
    _construct_field = False

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            abstract=False
        )
        options.graphql_type = None
        options.interfaces = []
        return options

    def construct(cls, bases, attrs):
        if not cls._meta.abstract:
            Input = attrs.pop('Input', None)
            input_fields = props(Input) if Input else {}

            cls.mutate_and_get_payload = attrs.pop('mutate_and_get_payload', None)

            input_local_fields = copy_fields(InputField, get_fields(InputObjectType, input_fields, ()))
            local_fields = cls._extract_local_fields(attrs)
            assert cls.mutate_and_get_payload, "{}.mutate_and_get_payload method is required in a ClientIDMutation ObjectType.".format(cls.__name__)
            field = mutation_with_client_mutation_id(
                name=cls._meta.name or cls.__name__,
                input_fields=input_local_fields,
                output_fields=cls._fields(bases, attrs, local_fields),
                mutate_and_get_payload=cls.mutate_and_get_payload,
            )
            cls._meta.graphql_type = field.type
            cls.Field = partial(Field.copy_and_extend, field, type=field.type, _creation_counter=None)
        constructed = super(ClientIDMutationMeta, cls).construct(bases, attrs)
        return constructed


class ClientIDMutation(six.with_metaclass(ClientIDMutationMeta, Mutation)):
    class Meta:
        abstract = True
