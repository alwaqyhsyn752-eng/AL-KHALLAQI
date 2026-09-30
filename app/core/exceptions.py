"""Custom exceptions."""
from typing import Optional


class HKBaseError(Exception):
    status_code: int = 500
    message: str = "Internal error"

    def __init__(self, message: Optional[str] = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class ConfigurationError(HKBaseError):
    status_code = 500
    message = "Configuration error"


class ProviderError(HKBaseError):
    status_code = 502
    message = "AI provider error"


class ToolError(HKBaseError):
    status_code = 400
    message = "Tool execution error"


class NotFoundError(HKBaseError):
    status_code = 404
    message = "Resource not found"


class AuthError(HKBaseError):
    status_code = 401
    message = "Unauthorized"


class ValidationError(HKBaseError):
    status_code = 422
    message = "Validation error"


class AgentMaxStepsError(HKBaseError):
    status_code = 422
    message = "Agent reached maximum steps"
