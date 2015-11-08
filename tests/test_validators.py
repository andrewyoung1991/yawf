import pytest

from yawf.schemas import validators


@pytest.mark.parametrize("validator, arg, expect", [
    (validators.MinLengthValidator(length=2), [1, 2], False),
    (validators.MaxLengthValidator(length=2), [1,], False),
    (validators.MinLengthValidator(length=2), [1,], True),
    (validators.MaxLengthValidator(length=2), [1, 2, 3], True),
    (validators.MinValidator(value=2), 2, False),
    (validators.MaxValidator(value=2), 1, False),
    (validators.MinValidator(value=2), 1, True),
    (validators.MaxValidator(value=2), 3, True),
    ])
def test_validator(validator, arg, expect):
    if expect:
        with pytest.raises(AssertionError):
            validator.validate(arg)
    else:
        assert validator.validate(arg) == arg


def test_base_validator():
    validator = validators.Validator()
    with pytest.raises(NotImplementedError):
        validator.validate(1)

    assert validator.dump_schema() == {}


@pytest.mark.parametrize("validator, expect", [
    (validators.MinLengthValidator(length=2), {"min-length": 2}),
    (validators.MaxLengthValidator(length=2), {"max-length": 2}),
    (validators.MinValidator(value=2), {"min": 2}),
    (validators.MaxValidator(value=2), {"max": 2}),
    ])
def test_dump_schema(validator, expect):
    assert validator.dump_schema() == expect
