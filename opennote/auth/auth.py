import hashlib
import uuid
from datetime import datetime
from typing import Union, Literal

from flask import Blueprint, Response
from pydantic import BaseModel

from .jwt import JWT
from opennote.common.error_handling import ClientError
from opennote.common.routing_decorators import json_serialization
from opennote.database import db
from opennote.db_model import User

URL_PREFIX = '/access-token'

bluprint_auth = Blueprint('access_token', __name__, url_prefix=URL_PREFIX)
bluprint_users = Blueprint('users', __name__, url_prefix='/users')


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


class AuthClientError(ClientError[Literal["VALIDATION_ERROR"]]):
    pass


@bluprint_users.post('/')
@json_serialization
def register(body: RegisterRequest) -> tuple[Response, int]:
    salt = str(uuid.uuid4()).replace("-", "")
    if db.session.query(User).filter_by(username=body.username).first():
        raise AuthClientError(code="VALIDATION_ERROR", status_code=400)
    db.session.add(
        User(id=uuid.uuid4(), username=body.username, password_salt=salt, password=hash_password(body.password, salt)))
    db.session.commit()
    return Response(), 201


@bluprint_auth.post('/')
@json_serialization
def login(body: LoginRequest) -> tuple[Union[TokenResponse, Response], int]:
    user = db.session.query(User).filter_by(username=body.username).first()
    if not user:
        return Response(), 403
    if hash_password(body.password, user.password_salt) != user.password:
        return Response(), 403

    token: JWT = JWT.create(issued_at=int(datetime.now().timestamp()), token_id=str(uuid.uuid4()))
    return TokenResponse(token='Bearer ' + token.serialize()), 200


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
