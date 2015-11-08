"""
"""
import datetime


def _dict_merge(a, b):
    c = a.copy()
    c.update(b)
    return c


class Field:
    """ base class for a field on a schema. fields have two jobs, to clean
    and validate data.
    """
    TYPE = None
    PYTYPES = None  # a tuple of primitive types
    VALIDATORS = []

    def __init__(self, required=True, help_text=None, validators=None):
        self.required = required
        self.help_text = help_text
        self.validators = self.VALIDATORS[:]
        self._value = None

        if validators is not None:
            self.validators.extend(validators)

    def __set__(self, instance, value):
        self._value = self.validate(value)
        return self._value

    def __get__(self, instance, owner):
        return self._value

    def validate(self, value):
        cleaned = self.clean(value)
        for validator in self.validators:
            validator.validate(cleaned)
        return cleaned

    def dump_schema(self):
        schema = {
            "type": self.TYPE,
            "required": self.required,
            "description": self.help_text
            }
        for validator in self.validators:
            schema = _dict_merge(schema, validator.dump_schema())
        return schema


class NestedField(Field):
    TYPE = "object"

    def __init__(self, nested, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nested = nested

    def validate(self, value):
        if not isinstance(value, self.nested):
            if isinstance(value, dict):
                value = self.nested(**value)
            else:
                raise TypeError("{0} is not of type"
                    " {1}".format(value, self.TYPE))
        for validator in self.validators:  # pragma: no cover
            validator.validate(value)
        return value

    def dump_schema(self):
        schema = super().dump_schema()
        schema = _dict_merge(self.nested.dump_schema(), schema)
        return schema


class StringField(Field):
    TYPE = "string"
    PYTYPES = (str, )

    def clean(self, value):
        if isinstance(value, bytes):
            cleaned = value.decode("utf-8")
        else:
            cleaned = str(value)
        return cleaned


class IntField(Field):
    TYPE = "int"
    PYTYPES = (int, )

    def clean(self, value):
        cleaned = int(value)
        return cleaned


class FloatField(Field):
    TYPE = "float"
    PYTYPES = (float, int)

    def clean(self, value):
        cleaned = float(value)
        return cleaned


class BoolField(Field):
    TYPE = "bool"
    PYTYPES = (bool, )

    def clean(self, value):
        cleaned = bool(value)
        return cleaned


class ListField(Field):
    TYPE = "array"
    PYTYPES = (list, set, tuple)

    def clean(self, value):
        cleaned = list(value)
        return cleaned


class SetField(ListField):
    def clean(self, value):
        cleaned = list(set(value))
        return cleaned

    def dump_schema(self):
        schema = super().dump_schema()
        schema["uniqueItems"] = True
        return schema


class DatetimeField(Field):
    TYPE = "date-time"
    PYTYPES = (datetime.datetime, )

    def clean(self, value):
        if isinstance(value, datetime.datetime):
            return value
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')


class TypedListSchemaMixin:
    def dump_schema(self):
        schema = super().dump_schema()
        schema["items"] = {"type": self.LISTTYPE}
        return schema


class TypedListField(TypedListSchemaMixin, ListField):
    LISTTYPE = None
    PYLISTTYPE = None

    def clean(self, value):
        cleaned = super().clean(value)
        return list(map(lambda x: self.PYLISTTYPE(x), cleaned))


class TypedSetField(TypedListSchemaMixin, SetField):
    LISTTYPE = None
    PYLISTTYPE = None

    def clean(self, value):
        cleaned = super().clean(value)
        return list(map(lambda x: self.PYLISTTYPE(x), cleaned))
