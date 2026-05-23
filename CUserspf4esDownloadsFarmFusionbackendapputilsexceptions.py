"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status


class FarmFusionException(HTTPException):
    """Base exception for FarmFusion API."""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationError(FarmFusionException):
    """Authentication related errors."""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class PermissionDenied(FarmFusionException):
    """Permission related errors."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class ResourceNotFound(FarmFusionException):
    """Resource not found errors."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(FarmFusionException):
    """Validation errors."""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
