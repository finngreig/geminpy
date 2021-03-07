from enum import Enum


class ResponseCodes(Enum):
    INPUT = 10
    SUCCESS = 20
    REDIRECT = 30
    TEMPORARY_FAILURE = 40
    PERMANENT_FAILURE = 50
    # CLIENT_CERTIFICATE_REQUIRED = 60 (future)


class Response:

    def __init__(self, code, meta, body=None):
        self.code = code
        self.meta = meta
        self.body = body

    def encode(self):
        return str.encode(f"{self.code.value} {self.meta}\r\n{self.body if self.body else ''}")
