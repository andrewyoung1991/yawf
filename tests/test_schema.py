import pytest

from yawf import schemas
from yawf.schemas.validators import MinLengthValidator, MaxLengthValidator


@pytest.fixture
def Schema():

    class MySchema(schemas.MessageSchema):
        id = schemas.IntField(help_text="users unique id")
        name = schemas.StringField(help_text="users first and last name")
        message = schemas.StringField(validators=[
            MinLengthValidator(length=5),
            MaxLengthValidator(length=120),
            ])

    return MySchema


def test_schema(Schema):
    schema = Schema.dump_schema()
    expect = {
        "type": "object",
        "properties": {
            "id": {
                "type": "int",
                "required": True,
                "description": "users unique id"
                },
            "name": {
                "type": "string",
                "required": True,
                "description": "users first and last name"
                },
            "message": {
                "type": "string",
                "required": True,
                "description": None,
                "min-length": 5,
                "max-length": 120
                },
            }
        }
    assert schema == expect


def test_valid_schema(Schema):
    schema = Schema(id=2)
    schema.name = "brain boy"
    schema.message = "test test test"

    dumped = schema.dump_dict()
    assert dumped["id"] == schema.id
    assert dumped["name"] == schema.name
    assert dumped["message"] == schema.message

    dumped_json = Schema.dumps(schema)
    assert isinstance(dumped_json, str)

    same_schema = Schema.loads(dumped_json)
    assert schema == same_schema


def test_invalid_schema(Schema):
    schema = Schema()
    with pytest.raises(AssertionError) as err:
        schema.pony = "twinkle"
        assert err == "pony is not a valid field for Schema"


def test_nested_schema(Schema):
    class ASchema(schemas.MessageSchema):
        price = schemas.FloatField(required=False)
        schema = schemas.NestedField(nested=Schema,
            help_text="a nested schema")

    expect = {
        "type": "object",
        "properties": {
            "price": {
                "type": "float",
                "required": False,
                "description": None
                },
            "schema": {
                "type": "object",
                "required": True,
                "description": "a nested schema",
                "properties": {
                    "id": {
                        "type": "int",
                        "required": True,
                        "description": "users unique id"
                        },
                    "name": {
                        "type": "string",
                        "required": True,
                        "description": "users first and last name"
                        },
                    "message": {
                        "type": "string",
                        "required": True,
                        "description": None,
                        "min-length": 5,
                        "max-length": 120
                        },
                    }
                }
            }
        }
    assert ASchema.dump_schema() == expect


def test_valid_nested_schema(Schema):
    class ASchema(schemas.MessageSchema):
        price = schemas.FloatField(required=False)
        schema = schemas.NestedField(nested=Schema,
            help_text="a nested schema")

    message = ASchema(price=4.5)
    message.schema = Schema(id=2, name="test", message="okayyy")

    dumped = message.dump_dict()
    assert dumped["price"] == message.price
    assert dumped["schema"]["id"] == message.schema.id
    assert dumped["schema"]["name"] == message.schema.name
    assert dumped["schema"]["message"] == message.schema.message

    dumped_json = ASchema.dumps(message)
    assert isinstance(dumped_json, str)

    same_schema = ASchema.loads(dumped_json)
    assert message == same_schema
