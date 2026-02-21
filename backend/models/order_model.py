"""Order Model - Customer orders"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base


class Order(Base):
	__tablename__ = "orders"

	order_id = Column(String(20), primary_key=True)
	engineer_id = Column(String(20), ForeignKey("users.user_id"), nullable=False, index=True)
	station_id = Column(String(20), ForeignKey("stations.station_id"), nullable=False)
	priority = Column(String(10), default="Regular")
	status = Column(String(20), default="Placed", index=True)
	runner_id = Column(String(20), ForeignKey("users.user_id"), nullable=True, index=True)
	special_instructions = Column(String(500), nullable=True)
	total_price = Column(Float, nullable=True)
	ai_predicted_eta = Column(Integer, nullable=True)
	actual_delivery_time = Column(Integer, nullable=True)
	cancelled_reason = Column(String(200), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
	delivered_at = Column(DateTime(timezone=True), nullable=True)

	# Relationships
	items = relationship("OrderItem", backref="order", lazy="joined")
	status_history = relationship("OrderStatusHistory", backref="order", lazy="dynamic")

	def __repr__(self):
		return f"<Order {self.order_id} - {self.status}>"

	def to_dict(self):
		return {
			"order_id": self.order_id,
			"engineer_id": self.engineer_id,
			"station_id": self.station_id,
			"priority": self.priority,
			"status": self.status,
			"runner_id": self.runner_id,
			"special_instructions": self.special_instructions,
			"total_price": self.total_price,
			"ai_predicted_eta": self.ai_predicted_eta,
			"actual_delivery_time": self.actual_delivery_time,
			"cancelled_reason": self.cancelled_reason,
			"created_at": str(self.created_at),
			"updated_at": str(self.updated_at),
			"delivered_at": str(self.delivered_at) if self.delivered_at else None,
			"items": [item.to_dict() for item in self.items] if self.items else []
		}

