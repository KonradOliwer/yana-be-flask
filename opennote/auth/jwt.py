import hashlib
import hmac
import json
import numbers
from base64 import b64encode, b64decode
from datetime import datetime

from flask import current_app
from uuid import UUID, uuid4


def timestamp_in_seconds() -> int:
    return int(datetime.now().timestamp())


class InvalidJWT(Exception):
    def __init__(self, message: str):
        self.message = message


class JWT:
    SUPPORTED_ALGORITHM = "RS256"
    STRING_ENCODING = 'utf-8'
    TIME_TO_LIVE = 1800  # in seconds; 30 min
    _ALGORITHM = "alg"
    _ISSUED_AT = "jti"
    _TOKE_ID = "iat"
    _USER_ID = "user_id"

    def __init__(self, expire_at: int = None, token_id: UUID = None, user_id: UUID = None, algorith: str = None, signature: str = None):
        self.expire_at = expire_at
        self.token_id = token_id  # for now not in use, but adds random element, which helps with countering rainbow tables
        self.user_id = user_id
        self.algorith = algorith
        self._signature = signature

    @classmethod
    def create(cls, issued_at: int, user_id: UUID, token_id: UUID) -> 'JWT':
        return cls(expire_at=issued_at + JWT.TIME_TO_LIVE, token_id=token_id, user_id=user_id, algorith=JWT.SUPPORTED_ALGORITHM)

    @classmethod
    def from_string(cls, token: str) -> 'JWT':
        try:
            header, payload, signature = token.split('.')
            header_json = JWT._dict_from_b64_json(header)
            payload_json = JWT._dict_from_b64_json(payload)
            return cls(algorith=header_json[JWT._ALGORITHM], expire_at=payload_json[JWT._ISSUED_AT],
                       token_id=UUID(payload_json[JWT._TOKE_ID]), user_id=UUID(payload_json[JWT._USER_ID]), signature=signature)
        except:
            raise InvalidJWT("parsing error")

    def serialize(self) -> str:
        return f"{self.header}.{self.payload}.{self.signature}"

    def validate(self):
        if self.algorith != JWT.SUPPORTED_ALGORITHM:
            raise InvalidJWT("unsupported algorith")
        if not isinstance(self.expire_at, numbers.Number):
            raise AttributeError("issued_at is not a number")
        if not hmac.compare_digest(self.signature, self._generate_signature()):
            raise InvalidJWT("invalid signature")

    @property
    def is_expired(self) -> bool:
        return timestamp_in_seconds() > self.expire_at

    @property
    def header(self) -> str:
        return JWT._object_to_json_b64({
            JWT._ALGORITHM: self.algorith
        })

    @property
    def payload(self) -> str:
        return JWT._object_to_json_b64({
            JWT._ISSUED_AT: self.expire_at,
            JWT._TOKE_ID: str(self.token_id or uuid4()),
            JWT._USER_ID: str(self.user_id),
        })

    @property
    def signature(self) -> str:
        return self._signature or self._generate_signature()

    @classmethod
    def _object_to_json_b64(cls, obj):
        return b64encode(json.dumps(obj).encode(JWT.STRING_ENCODING)).decode(JWT.STRING_ENCODING)

    @classmethod
    def _dict_from_b64_json(cls, b64):
        return json.loads(b64decode(b64).decode(JWT.STRING_ENCODING))

    def _generate_signature(self) -> str:
        return b64encode(hmac.new(
            key=bytes(current_app.config.get("JWT_SECRET"), JWT.STRING_ENCODING),
            msg=bytes(f"{self.header}.{self.payload}", JWT.STRING_ENCODING),
            digestmod=hashlib.sha256
        ).digest()).decode(JWT.STRING_ENCODING)
