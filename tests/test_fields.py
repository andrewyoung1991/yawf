from datetime import datetime

import pytest

from yawf.schemas import fields, validators


@pytest.mark.parametrize("field, value, expect", [
    (fields.StringField(), "penguin", False),
    (fields.IntField(), 1, False),
    (fields.FloatField(), 1.0, False),
    (fields.BoolField(), True, False),
    (fields.ListField(), [1, 2, 3], False),
    (fields.SetField(), [1, 2, 3], False),
    (fields.DatetimeField(), datetime.now(), False),
    (fields.NestedField(nested=dict), {"ping": "pong"}, False),

    (fields.IntField(), "fourty", True),
    (fields.FloatField(), "three.four", True),
    (fields.ListField(), 1, True),
    (fields.SetField(), 1, True),
    (fields.NestedField(nested=dict), 3, True),
    ])
def test_validate_fields(field, value, expect):
    if expect is True:
        with pytest.raises((ValueError, TypeError)):
            field.validate(value)
    else:
        assert field.validate(value) == value


def test_clean_bytestring():
    field = fields.StringField()
    assert field.clean(b"penguin") == "penguin"

def test_clean_datestring():
    now = datetime.utcnow()
    field = fields.DatetimeField()
    assert field.clean(now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")) == now

@pytest.mark.parametrize("field, expect", [
    (fields.StringField(), {"type": "string", "required": True, "description": None}),
    (fields.IntField(), {"type": "int", "required": True, "description": None}),
    (fields.FloatField(), {"type": "float", "required": True, "description": None}),
    (fields.BoolField(), {"type": "bool", "required": True, "description": None}),
    (fields.ListField(), {"type": "array", "required": True, "description": None}),
    (fields.SetField(), {"type": "array", "required": True, "description": None, "uniqueItems": True}),
    (fields.DatetimeField(), {"type": "date-time", "required": True, "description": None}),
    ])
def test_dump_schema(field, expect):
    assert field.dump_schema() == expect


def test_minlen_string():
    field = fields.StringField(validators=[validators.MinLengthValidator(length=2)])
    with pytest.raises(AssertionError):
        field.validate("1")
    schema = {"type": "string", "required": True, "description": None, "min-length": 2}
    assert field.dump_schema() == schema


def test_typed_list():
    class IntListField(fields.TypedListField):
        LISTTYPE = "int"
        PYLISTTYPE = int

    field = IntListField()
    assert field.validate([1, 2, 3]) == [1, 2, 3]

    with pytest.raises(ValueError):
        field.validate(["one", "two"])

    schema = {"type": "array", "required": True, "description": None, "items": {"type": "int"}}
    assert field.dump_schema() == schema

def test_typed_set():
    class IntSetField(fields.TypedSetField):
        LISTTYPE = "int"
        PYLISTTYPE = int

    field = IntSetField()
    assert field.validate([1, 2, 2, 3]) == [1, 2, 3]

    with pytest.raises(ValueError):
        field.validate(["one", "two"])

    schema = {"type": "array", "required": True, "description": None, "items": {"type": "int"}, "uniqueItems": True}
    assert field.dump_schema() == schema
