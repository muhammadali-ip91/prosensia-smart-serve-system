"""Error Response Schemas"""

from pydantic import BaseModel
from typing import Optional, Any


class ErrorDetail(BaseModel):
	code: str
	message: str
	details: Optional[Any] = None


class ErrorResponse(BaseModel):
	success: bool = False
	error: ErrorDetail
	timestamp: Optional[str] = None
	request_id: Optional[str] = None

