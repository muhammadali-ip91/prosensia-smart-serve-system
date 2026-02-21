"""Notification Model - System notifications for all users"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class Notification(Base):
	__tablename__ = "notifications"

	notification_id = Column(Integer, primary_key=True, autoincrement=True)
	user_id = Column(String(20), ForeignKey("users.user_id"), nullable=False, index=True)
	type = Column(String(50), nullable=False)
	title = Column(String(200), nullable=False)
	message = Column(String(500), nullable=False)
	priority = Column(String(10), default="normal")
	is_read = Column(Boolean, default=False, index=True)
	action_url = Column(String(200), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	def __repr__(self):
		return f"<Notification {self.notification_id} - {self.title}>"

	def to_dict(self):
		return {
			"notification_id": self.notification_id,
			"user_id": self.user_id,
			"type": self.type,
			"title": self.title,
			"message": self.message,
			"priority": self.priority,
			"is_read": self.is_read,
			"action_url": self.action_url,
			"created_at": str(self.created_at)
		}

