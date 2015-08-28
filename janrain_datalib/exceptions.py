"""Exceptions this package may throw."""

class ApiError(Exception):
    """Generic error thrown by an api call."""
    def __init__(self, message, code):
        super(ApiError, self).__init__(message, code)
        self.message = message
        self.code = code

class ApiAuthError(ApiError):
    """Authentication error."""
    pass

class ApiInputError(ApiError):
    """Input was invalid."""
    pass

class ApiUpdateError(ApiError):
    """Update failed."""
    pass

class ApiNotFoundError(ApiError):
    """Result not found."""
    pass

class ApiTooLargeError(ApiError):
    """The request payload was too large."""
    pass

class ApiRateLimitError(ApiError):
    """The call exceeded the app's rate limit."""
    pass

class AlreadyExistsError(ValueError):
    """Tried to create something that already exists."""
    pass

class InputError(ValueError):
    """Input was invalid."""
    pass

class NotFoundError(LookupError):
    """Result not found."""
    pass

