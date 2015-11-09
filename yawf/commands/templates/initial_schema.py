from yawf import schemas

class Hello(schemas.MessageSchema):
    message = schemas.StringField()
