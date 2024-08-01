import hashlib
from typing import Union, Literal

from flask import Blueprint, Response, Flask, jsonify, request
from pydantic import BaseModel
from uuid import uuid4, UUID

from opennote.common.data_time_utils import timestamp_in_seconds, timestamp_to_cookie_expires_format, PAST_TIME_EXPIRE_AT_COOKIE_VALUE
from opennote.common.error_handling import ClientError
from opennote.common.routing_decorators import endpoint
from opennote.database import db
from opennote.db_model import User, RefreshToken
from .jwt import JWT

ACCESS_TOKEN_PREFIX = '/access-token'
LOGIN_ROUTE_POSTFIX = '/login'
LOGIN_ROUTE = ACCESS_TOKEN_PREFIX + LOGIN_ROUTE_POSTFIX

bluprint_auth = Blueprint('access_token', __name__, url_prefix=ACCESS_TOKEN_PREFIX)
bluprint_users = Blueprint('users', __name__, url_prefix='/users')


class AuthRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    token_expire_at: int


class RegisterRequest(BaseModel):
    username: str
    password: str


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
@endpoint
def register(body: RegisterRequest) -> tuple[Response, int]:
    salt = create_salt()
    if db.session.query(User).filter_by(username=body.username).first():
        raise AuthClientError(code="VALIDATION_ERROR", status_code=400)
    db.session.add(
        User(id=uuid4(), username=body.username, password_salt=salt, password=hash_password(body.password, salt)))
    db.session.commit()
    return Response(), 201


@bluprint_users.get('/whoami')
@endpoint
def whoami(jwt: JWT) -> tuple[UserResponse, int]:
    user = db.session.query(User).get(jwt.user_id)
    return UserResponse(username=user.username), 200


@bluprint_auth.post(LOGIN_ROUTE_POSTFIX)
@endpoint
def create_token(body: AuthRequest) -> tuple[Union[AuthResponse, Response], int]:
    """

    :rtype: object
    """
    user = db.session.query(User).filter_by(username=body.username).first()
    if not user:
        return Response(), 403
    if hash_password(body.password, user.password_salt) != user.password:
        return Response(), 403

    token = create_new_token_with_refresh_token_persisted(user.id)
    response = create_auth_response(token)
    db.session.commit()
    return response, 201


@bluprint_auth.post('/refresh')
@endpoint
def preform_token_refresh(jwt: JWT) -> tuple[Union[AuthResponse, Response], int]:
    refresh_token = db.session.query(RefreshToken).get(jwt.refresh_token)
    if refresh_token.expire_at < timestamp_in_seconds() or not refresh_token.active:
        return Response(), 403
    refresh_token.active = False

    token = create_new_token_with_refresh_token_persisted(user_id=jwt.user_id)
    response = create_auth_response(token)
    db.session.commit()
    return response, 201


@bluprint_auth.post('/logout')
@endpoint
def delete_token(jwt: JWT) -> tuple[Union[AuthResponse, Response], int]:
    refresh_token = db.session.query(RefreshToken).get(jwt.refresh_token)
    refresh_token.active = False

    response = Response()
    response.headers.add('Set-Cookie', f"Authorization=deleted; HttpOnly; SameSite=Strict; Secure; Path=/; Expires={PAST_TIME_EXPIRE_AT_COOKIE_VALUE}")
    return response, 204


def create_auth_response(token):
    body = AuthResponse(token_expire_at=token.expire_at)
    response = jsonify(body)
    response.headers.add('Set-Cookie',
                         f"Authorization=Bearer {token.serialize()}; HttpOnly; SameSite=Strict; Secure; Path=/; Expires={timestamp_to_cookie_expires_format(token.expire_at)}")
    return response


def create_new_token_with_refresh_token_persisted(user_id: UUID) -> JWT:
    refresh_token = RefreshToken(user_id=user_id, expire_at=timestamp_in_seconds() + JWT.REFRESH_TOKEN_TTL)
    db.session.add(refresh_token)

    token = JWT.create(issued_at=timestamp_in_seconds(), refresh_token=refresh_token.id, user_id=user_id)
    return token


def create_salt():
    return str(uuid4()).replace("-", "")


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()
