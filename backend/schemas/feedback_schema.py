"""Feedback Schemas"""

from pydantic import BaseModel, Field
from typing import Optional


class FeedbackRequest(BaseModel):
	rating: int = Field(ge=1, le=5)
	comment: Optional[str] = None


class FeedbackResponse(BaseModel):
	feedback_id: int
	order_id: str
	engineer_id: str
	rating: int
	comment: Optional[str] = None
	created_at: str

