import hashlib
from typing import Union, Literal

from flask import Blueprint, Response, Flask, jsonify, request
from pydantic import BaseModel
from uuid import uuid4, UUID

from opennote.common.error_handling import ClientError
from opennote.common.routing_decorators import json_serialization
from opennote.database import db
from opennote.db_model import User
from .jwt import JWT, timestamp_in_seconds

URL_PREFIX = '/access-token'

bluprint_auth = Blueprint('access_token', __name__, url_prefix=URL_PREFIX)
bluprint_users = Blueprint('users', __name__, url_prefix='/users')


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token_expire_at: int


class UserResponse(BaseModel):
    username: str


class AuthClientError(ClientError[Literal["VALIDATION_ERROR"]]):
    pass


def init_starting_data(app: Flask):
    id = UUID("a155d430-fac1-489c-8d2b-634808e04bd6")
    username = "admin"
    password = "admin"
    with app.app_context():
        existing_user = db.session.query(User).filter_by(username=username).first()
        if not existing_user:
            salt = create_salt()
            hashed_password = hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
            db.session.add(User(id=id, username=username, password_salt=salt, password=hashed_password))
            db.session.commit()


@bluprint_users.post('/')
@json_serialization
def register(body: RegisterRequest) -> tuple[Response, int]:
    salt = create_salt()
    if db.session.query(User).filter_by(username=body.username).first():
        raise AuthClientError(code="VALIDATION_ERROR", status_code=400)
    db.session.add(
        User(id=uuid4(), username=body.username, password_salt=salt, password=hash_password(body.password, salt)))
    db.session.commit()
    return Response(), 201


@bluprint_users.get('/whoami')
@json_serialization
def whoami() -> tuple[UserResponse, int]:
    _, token = request.cookies.get('Authorization').split(' ')
    jwt = JWT.from_string(token)
    user = db.session.query(User).get(jwt.user_id)
    return UserResponse(username=user.username), 200


@bluprint_auth.post('/')
@json_serialization
def login(body: LoginRequest) -> tuple[Union[LoginResponse, Response], int]:
    user = db.session.query(User).filter_by(username=body.username).first()
    if not user:
        return Response(), 403
    if hash_password(body.password, user.password_salt) != user.password:
        return Response(), 403

    token = JWT.create(issued_at=timestamp_in_seconds(), token_id=str(uuid4()), user_id=user.id)
    body = LoginResponse(token_expire_at=token.expire_at)
    response = jsonify(body)
    response.headers.add('Set-Cookie', f"Authorization=Bearer {token.serialize()}; HttpOnly; SameSite=Strict; Secure; Path=/; Max-Age={JWT.TIME_TO_LIVE}")
    return response, 201


def create_salt():
    return str(uuid4()).replace("-", "")


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
