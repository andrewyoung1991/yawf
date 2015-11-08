class Validator:
    def validate(self, value):
        raise NotImplementedError

    def dump_schema(self):
        return {}


class LengthValidator(Validator):
    KEYNAME = None

    def __init__(self, length):
        self.length = length

    def validate(self, value):
        assert self.is_valid(value)
        return value

    def dump_schema(self):
        return {self.KEYNAME: self.length}


class MinLengthValidator(LengthValidator):
    KEYNAME = "min-length"

    def is_valid(self, value):
        return self.length <= len(value)


class MaxLengthValidator(LengthValidator):
    KEYNAME = "max-length"

    def is_valid(self, value):
        return len(value) <= self.length


class NumberValidator(Validator):
    KEYNAME = None

    def __init__(self, value):
        self.value = value

    def validate(self, value):
        assert self.is_valid(value)
        return value

    def dump_schema(self):
        return {self.KEYNAME: self.value}


class MinValidator(NumberValidator):
    KEYNAME = "min"

    def is_valid(self, value):
        return self.value <= value


class MaxValidator(NumberValidator):
    KEYNAME = "max"

    def is_valid(self, value):
        return value <= self.value
