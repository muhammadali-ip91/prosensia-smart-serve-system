"""Notification Schemas"""

from pydantic import BaseModel
from typing import Optional


class NotificationResponse(BaseModel):
	notification_id: int
	type: str
	title: str
	message: str
	priority: str
	is_read: bool
	action_url: Optional[str] = None
	created_at: str


class MarkReadRequest(BaseModel):
	notification_ids: list[int]

