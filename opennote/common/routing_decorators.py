from functools import wraps

from flask import request, jsonify, Response

from opennote.auth.auth_filter import extract_jwt_from_request, AuthException


def endpoint(func):
    """
    This decorator provide following functionalities:
    \b
    - If your function has 'body' parameter which is not provided by route (ex. by path param), then body of given time will be pulled from request using provided type and provided to function
    \b
    - If your function has 'jwt' parameter and request contains jwt, it will be extracted from request and provided to function
    \b
    - If first element of return type tuple is not flask.Response, this part of return type will be transformed to response with json made from this element
    """

    @wraps(func)
    def decorated_function(*args: any, **kwargs: any) -> tuple[Response, int]:
        fun_kwargs = kwargs if "body" not in func.__annotations__ else kwargs | {
            'body': func.__annotations__["body"](**request.get_json())}
        try:
            fun_kwargs = fun_kwargs if "jwt" not in func.__annotations__ else fun_kwargs | {
                'jwt': extract_jwt_from_request()}
        except AuthException:
            pass

        result, status = func(*args, **fun_kwargs)
        if isinstance(result, Response):
            return result, status
        return jsonify(result), status

    return decorated_function
