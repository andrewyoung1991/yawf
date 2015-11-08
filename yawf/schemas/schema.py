""" this module is not interested in an implementation of the JSON schema drafts
instead it implements MessageSchema, which validate the transmission of messages
about your websocket api.
"""
import json
import datetime
from collections import OrderedDict

from yawf.utils import Frozen

from . import fields


class FieldsDict(OrderedDict):
    def __init__(self, *, fields):
        super().__init__(**fields)
        self.fields_list = list(self.keys())
        self.required_fields = {key: value for key, value in self.items() if\
                                getattr(value, "required") is True}

    __getattr__ = dict.__getitem__


class MessageSchemaMeta(type):
    def __new__(cls, name, bases, kwargs):
        super_new = super().__new__

        _fields = {}
        for key, value in kwargs.items():
            if isinstance(value, fields.Field):
                _fields[key] = value
        _fields = Frozen(FieldsDict(fields=_fields))
        kwargs["_fields"] = _fields

        return super_new(cls, name, bases, kwargs)


class MessageSchema(metaclass=MessageSchemaMeta):
    """
    """
    TYPE = "object"

    class UnknownFieldError(KeyError): pass

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __setattr__(self, key, value):
        assert key in self._fields.fields_list, "{0} is not a valid "\
            "field for {1}".format(key, self.__class__.__name__)
        return super().__setattr__(key, value)

    def __str__(self):
        return "{0}".format(self.dump_dict())

    def __eq__(self, other):
        return str(self) == str(other)

    def _validate_required(self):
        for field in self._fields.required_fields.keys():
            assert hasattr(self, field), "Field {} is required".format(field)

    @classmethod
    def dump_schema(cls):
        schema = {
            "type": "object",
            "properties": {}
            }
        for key, value in cls._fields.items():
            schema["properties"][key] = value.dump_schema()
        return schema

    def dump_dict(self):
        self._validate_required()
        schema = {}
        for key in self._fields.fields_list:
            value = getattr(self, key, None)
            if isinstance(value, MessageSchema):
                value = value.dump_dict()
            schema[key] = value
        return schema

    @classmethod
    def dumps(cls, message):
        serialized = message.dump_dict()
        return json.dumps(serialized, default=cls._default)

    @classmethod
    def loads(cls, message):
        loaded = json.loads(message)
        return cls(**loaded)

    @staticmethod
    def _default(obj):  # pragma: no cover
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
