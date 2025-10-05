class BloodAidException(Exception):
    """Base exception for BloodAid application"""
    def __init__(self, message: str, status_code: int = 400, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

class AuthenticationException(BloodAidException):
    """Authentication related exceptions"""
    def __init__(self, message: str = "Authentication failed", detail: str = None):
        super().__init__(message, 401, detail)

class AuthorizationException(BloodAidException):
    """Authorization related exceptions"""
    def __init__(self, message: str = "Access forbidden", detail: str = None):
        super().__init__(message, 403, detail)

class ValidationException(BloodAidException):
    """Validation related exceptions"""
    def __init__(self, message: str = "Validation failed", detail: str = None):
        super().__init__(message, 422, detail)

class NotFoundException(BloodAidException):
    """Resource not found exceptions"""
    def __init__(self, message: str = "Resource not found", detail: str = None):
        super().__init__(message, 404, detail)

class ConflictException(BloodAidException):
    """Conflict exceptions (duplicate data, etc.)"""
    def __init__(self, message: str = "Conflict detected", detail: str = None):
        super().__init__(message, 409, detail)

class ExternalServiceException(BloodAidException):
    """External service related exceptions"""
    def __init__(self, message: str = "External service error", detail: str = None):
        super().__init__(message, 502, detail)

class RateLimitException(BloodAidException):
    """Rate limiting exceptions"""
    def __init__(self, message: str = "Rate limit exceeded", detail: str = None):
        super().__init__(message, 429, detail)