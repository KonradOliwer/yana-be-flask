from typing import List

from flask import request, Response

from opennote.auth.jwt import JWT, InvalidJWT


class AuthException(Exception):
    pass


def creat_auth_filter(bypass_prefixes: List[str]):
    def auth_filter():
        for start_with in bypass_prefixes:
            if request.path.startswith(start_with):
                return
        if request.method == "OPTIONS":
            return
        try:
            jwt = extract_jwt_from_request()
            jwt.validate()
            if jwt.is_expired:
                raise AuthException("Expired token")
        except (AuthException, InvalidJWT) as error:
            return Response(), 403

    return auth_filter


def extract_jwt_from_request() -> JWT:
    try:
        auth_cookie = request.cookies.get('Authorization')
        auth_type, token = auth_cookie.split(' ')
    except (AttributeError, ValueError):
        raise AuthException("Invalid auth header")

    if auth_type != "Bearer":
        raise AuthException("Invalid auth type")

    try:
        return JWT.from_string(token)
    except InvalidJWT:
        raise AuthException("Invalid token")
