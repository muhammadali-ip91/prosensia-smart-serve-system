"""Feedback Model - Order feedback from engineers"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from database.connection import Base


class Feedback(Base):
	__tablename__ = "feedback"

	feedback_id = Column(Integer, primary_key=True, autoincrement=True)
	order_id = Column(String(20), ForeignKey("orders.order_id"), unique=True, nullable=False)
	engineer_id = Column(String(20), ForeignKey("users.user_id"), nullable=False, index=True)
	rating = Column(Integer, nullable=False)
	comment = Column(String(500), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())

	__table_args__ = (
		CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
	)

	def __repr__(self):
		return f"<Feedback {self.feedback_id} - Order:{self.order_id} Rating:{self.rating}>"

	def to_dict(self):
		return {
			"feedback_id": self.feedback_id,
			"order_id": self.order_id,
			"engineer_id": self.engineer_id,
			"rating": self.rating,
			"comment": self.comment,
			"created_at": str(self.created_at)
		}

