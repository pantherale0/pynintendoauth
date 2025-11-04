"""Nintendo auth exceptions."""


class HttpException(Exception):
    """A HTTP error occured"""

    def __init__(
        self, status_code: int, message: str, error_code: str | None = None
    ) -> None:
        """Initialize the exception."""
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.error_code = error_code

    def __str__(self) -> str:
        if self.error_code:
            return f"HTTP {self.status_code}: {self.message} ({self.error_code})"
        return f"HTTP {self.status_code}: {self.message}"


class InvalidSessionTokenException(HttpException):
    """Provided session token was invalid (invalid_grant)."""


class InvalidOAuthConfigurationException(HttpException):
    """The OAuth scopes are invalid."""
