import hashlib
import uuid
from datetime import datetime
from typing import Union

from flask import Blueprint, Response
from pydantic import BaseModel

from auth.jwt import JWT
from common.routing_decorators import json_serialization
from database import db
from opennote.db_model import User

URL_PREFIX = '/access_token'

bluprint = Blueprint('access_token', __name__, url_prefix=URL_PREFIX)


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


@bluprint.post('/register')
@json_serialization
def register(body: RegisterRequest) -> tuple[Response, int]:
    salt = str(uuid.uuid4()).replace("-", "")
    db.session.add(
        User(username=body.username, salt=salt, password=hash_password(body.password, salt)))
    db.session.commit()
    return Response(), 201


@bluprint.post('/')
@json_serialization
def login(body: LoginRequest) -> tuple[Union[TokenResponse, Response], int]:
    user = db.session.query(User).filter_by(User.username == body.username).first()
    if hash_password(body.password, user.password_salt) != user.password:
        return Response(), 401

    token: JWT = JWT.create(issued_at=int(datetime.now().timestamp()), token_id=str(uuid.uuid4()))
    return TokenResponse(token=token.serialize()), 200


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode("utf-8"))
