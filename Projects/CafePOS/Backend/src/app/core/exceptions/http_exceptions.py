from fastapi import HTTPException, status


class AppException(HTTPException):
    status_code = 400
    detail = "Error"
    headers = None

    def __init__(self, detail=None):
        super().__init__(
            status_code=self.status_code,
            detail=detail or self.detail,
            headers=self.headers
        )


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad Request!"


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Unauthorized!"
    headers = {"WWW-Authenticate": "Bearer"}


class ForbiddenException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Access Forbidden!"


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found!"


class DuplicateValueException(AppException):
    status_code = status.HTTP_409_CONFLICT
    detail = "Duplicate Value!"


class UnprocessableEntityException(AppException):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    detail = "Invalid data!"


class RateLimitException(AppException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests!"
    headers = {"Retry-After": "60"}


class InternalServerErrorException(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Internal server error!"


class CustomException(AppException):
    def __init__(self, status_code: int, detail: str, headers: dict | None = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__()