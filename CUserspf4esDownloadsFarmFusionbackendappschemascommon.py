"""
Common schemas used across the API.
"""
from typing import TypeVar, Generic, Optional, List
from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    pages: int
    has_next: bool
    has_prev: bool


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class FileUploadResponse(BaseModel):
    filename: str
    url: str
    size: int
    content_type: str
