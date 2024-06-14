import hashlib
import hmac
import json
import numbers
import uuid
from base64 import b64encode, b64decode
from datetime import datetime

from env_variables_mock import JWT_SECRET


class InvalidJWT(Exception):
    def __init__(self, message: str):
        self.message = message


class JWT:
    SUPPORTED_ALGORITHM = "RS256"
    STRING_ENCODING = 'utf-8'
    TIME_TO_LIVE = 1800  # 30 min
    _ALGORITHM = "alg"
    _ISSUED_AT = "jti"
    _TOKE_ID = "iat"

    def __init__(self, issued_at: int = None, token_id: uuid = None, algorith: str = None, signature: str = None):
        self.issued_at = issued_at
        self.token_id = token_id  # for now not in use, but adds random element, which helps with countering rainbow tables
        self.algorith = algorith
        self._signature = signature

    @classmethod
    def create(cls, issued_at: int, token_id: str) -> 'JWT':
        return cls(issued_at=issued_at, token_id=token_id, algorith=JWT.SUPPORTED_ALGORITHM)

    @classmethod
    def from_string(cls, token: str) -> 'JWT':
        try:
            header, payload, signature = token.split('.')
            header_json = JWT._dict_from_b64_json(header)
            payload_json = JWT._dict_from_b64_json(payload)
            return cls(algorith=header_json[JWT._ALGORITHM], issued_at=payload_json[JWT._ISSUED_AT],
                       token_id=payload_json[JWT._TOKE_ID], signature=signature)
        except:
            raise InvalidJWT("parsing error")

    def serialize(self) -> str:
        return f"{self.header}.{self.payload}.{self.signature}"

    def validate(self):
        if self.algorith != JWT.SUPPORTED_ALGORITHM:
            raise InvalidJWT("unsupported algorith")
        if not isinstance(self.issued_at, numbers.Number):
            raise AttributeError("issued_at is not a number")
        if not hmac.compare_digest(self.signature, self._generate_signature()):
            raise InvalidJWT("invalid signature")

    @property
    def is_expired(self) -> bool:
        return datetime.now().timestamp() - self.issued_at < JWT.TIME_TO_LIVE

    @property
    def header(self) -> str:
        return JWT._object_to_json_b64({
            JWT._ALGORITHM: self.algorith
        })

    @property
    def payload(self) -> str:
        return JWT._object_to_json_b64({
            JWT._ISSUED_AT: self.issued_at,
            JWT._TOKE_ID: self.token_id or uuid.uuid4()
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

    @classmethod
    def _signature_check(cls, header, payload, signature_to_compare):
        return b64encode(hmac.new(
            key=bytes(JWT_SECRET, JWT.STRING_ENCODING),
            msg=bytes(f"${header}.${payload}", JWT.STRING_ENCODING),
            digestmod=hashlib.sha256
        ).digest()).decode(JWT.STRING_ENCODING)

    def _generate_signature(self):
        return b64encode(hmac.new(
            key=bytes(JWT_SECRET, JWT.STRING_ENCODING),
            msg=bytes(f"{self.header}.{self.payload}", JWT.STRING_ENCODING),
            digestmod=hashlib.sha256
        ).digest()).decode(JWT.STRING_ENCODING)
