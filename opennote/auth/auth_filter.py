from typing import List

from flask import request, Response

from opennote.auth.jwt import JWT


def creat_auth_filter(bypass_prefixes: List[str]):
    def auth_filter():
        for start_with in bypass_prefixes:
            if request.path.startswith(start_with):
                return
        try:
            auth_cookie = request.cookies.get('Authorization')
            auth_type, token = auth_cookie.split(' ')
            if auth_type != "Bearer":
                raise Exception()
            try:
                jwt = JWT.from_string(token)
                jwt.validate()
                if jwt.is_expired:
                    raise Exception()
            except:
                return Response(), 403
        except:
            return Response(), 403

    return auth_filter
