from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import IntegrityError

from opennote.common.routing_decorators import json_serialization

T = TypeVar('T', bound=str)


class ClientError(Generic[T], Exception):
    def __init__(self, code: T, status_code: int, message: str = None):
        self.status_code = status_code
        self.message = message
        self.code = code


class ErrorResponse(BaseModel):
    message: str = None
    code: str


@json_serialization
def handle_client_error(e: ClientError) -> tuple[ErrorResponse, int]:
    if e.message:
        return ErrorResponse(code=e.code, message=e.message), e.status_code
    return ErrorResponse(code=e.code), e.status_code


@json_serialization
def handle_validation_error(error: ValidationError) -> tuple[ErrorResponse, int]:
    message = '\n'.join(f"{', '.join(e['loc'])}: {e['msg']}" for e in error.errors())
    return ErrorResponse(code="VALIDATION_ERROR", message=message), 400


@json_serialization
def handle_integrity_error(e: IntegrityError) -> tuple[ErrorResponse, int]:
    return ErrorResponse(code="WRITE_ERROR"), 400
