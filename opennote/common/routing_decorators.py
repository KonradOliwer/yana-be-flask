from functools import wraps

from flask import request, jsonify, Response






def json_serialization(func):

    @wraps(func)
    def decorated_function(*args: any, **kwargs: any) -> tuple[Response, int]:
        fun_kwargs = kwargs if "body" not in func.__annotations__ else kwargs | {
            'body': func.__annotations__["body"](**request.get_json())}
        result, status = func(*args, **fun_kwargs)
        return jsonify(result), status

    return decorated_function
