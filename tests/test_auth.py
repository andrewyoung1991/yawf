from datetime import datetime, timedelta

import pytest

import jwt

from yawf import auth
from yawf.conf import patch_settings


@pytest.fixture
def gen():
    return auth.JWTTokenAuth()

@patch_settings(secret_key="okay", token_valid_duration=timedelta(minutes=2))
def test_getting_token(gen):
    token = gen.create(username="fred", pk=9)
    assert token is not None

    validated = gen.validate(token)
    assert validated["username"] == "fred"
    assert validated["pk"] == 9
    assert datetime.now() < datetime.utcfromtimestamp(validated["exp"])

@patch_settings(secret_key="okay", token_valid_duration=timedelta(minutes=-1))
def test_expired_token(gen):
    token = gen.create(username="fred", pk=9)
    assert token is not None
    assert gen.validate(token) is None

    with pytest.raises(jwt.ExpiredSignatureError) as err:
        gen.refresh(token)
        assert err == "Signature has expired"

@patch_settings(secret_key="okay", token_valid_duration=timedelta(minutes=2))
def test_refreshing_token(gen):
    token = gen.create(username="fred", pk=9)
    assert token is not None

    validated = gen.validate(token)
    assert validated["username"] == "fred"
    assert validated["pk"] == 9
    assert datetime.now() < datetime.utcfromtimestamp(validated["exp"])

    cached = {}
    for key, value in validated.items():
        cached[key] = value

    token = gen.refresh(token)
    validate = gen.validate(token)
    assert cached["iat"] <= validated["iat"]
    assert cached["exp"] <= validated["exp"]
