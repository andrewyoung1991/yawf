import datetime

import jwt

from yawf.conf import settings


class JWTTokenAuth:
    """ a wrapper class around some jwt methods
    """
    def create(self, **payload):
        dur = settings.get("token_valid_duration") or datetime.timedelta(hours=1)
        now = datetime.datetime.utcnow()
        exp = now + dur
        payload.update({
            "exp": exp,
            "iat": now
            })
        return jwt.encode(payload, settings.secret_key)

    def refresh(self, token):
        validated = self.validate(token)
        if validated is not None:
            payload = {
                "username": validated["username"],
                "pk": validated["pk"]
                }
            return self.create(**payload)
        raise jwt.ExpiredSignatureError("Signature has expired")

    @staticmethod
    def validate(token):
        try:
            token = jwt.decode(token, settings.secret_key)
            return token
        except jwt.ExpiredSignatureError:
            return None
