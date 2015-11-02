import jwt

from yawf import settings


class JWTTokenAuth:
    def authenticate(token):
        jwt.parse(token, secret)

    def distribute_token():
        pass

    def refresh_token(token):
        pass
