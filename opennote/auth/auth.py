import hashlib
import uuid
from datetime import datetime
from typing import Union, Literal

from flask import Blueprint, Response, Flask
from pydantic import BaseModel

from .jwt import JWT, timestamp_in_seconds
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


def init_starting_data(app: Flask):
    username = "admin"
    password = "admin"
    with app.app_context():
        existing_user = db.session.query(User).filter_by(username=username).first()
        if not existing_user:
            user_id = uuid.uuid4()
            salt = str(uuid.uuid4()).replace("-", "")
            hashed_password = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
            db.session.add(User(id=user_id, username=username, password_salt=salt, password=hashed_password))
            db.session.commit()


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
    """

    :rtype: object
    """
    user = db.session.query(User).filter_by(username=body.username).first()
    if not user:
        return Response(), 403
    if hash_password(body.password, user.password_salt) != user.password:
        return Response(), 403

    token: JWT = JWT.create(issued_at=timestamp_in_seconds(), token_id=str(uuid.uuid4()))
    return TokenResponse(token= token.serialize()), 201


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
