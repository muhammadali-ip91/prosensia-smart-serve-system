"""Runner Model - Delivery runner details"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from database.connection import Base


class Runner(Base):
	__tablename__ = "runners"

	runner_id = Column(String(20), ForeignKey("users.user_id"), primary_key=True)
	current_status = Column(String(20), default="Available", index=True)
	active_order_count = Column(Integer, default=0)
	max_capacity = Column(Integer, default=5)
	current_location = Column(String(50), nullable=True)
	total_deliveries = Column(Integer, default=0)
	average_delivery_time = Column(Float, default=0.0)

	def __repr__(self):
		return f"<Runner {self.runner_id} - {self.current_status}>"

	def to_dict(self):
		return {
			"runner_id": self.runner_id,
			"current_status": self.current_status,
			"active_order_count": self.active_order_count,
			"max_capacity": self.max_capacity,
			"current_location": self.current_location,
			"total_deliveries": self.total_deliveries,
			"average_delivery_time": self.average_delivery_time
		}

