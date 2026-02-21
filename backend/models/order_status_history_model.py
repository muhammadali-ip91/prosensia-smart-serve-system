"""Order Status History Model - Audit trail for order status changes"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class OrderStatusHistory(Base):
	__tablename__ = "order_status_history"

	history_id = Column(Integer, primary_key=True, autoincrement=True)
	order_id = Column(String(20), ForeignKey("orders.order_id"), nullable=False, index=True)
	old_status = Column(String(20), nullable=True)
	new_status = Column(String(20), nullable=False)
	changed_by = Column(String(20), ForeignKey("users.user_id"), nullable=False)
	changed_at = Column(DateTime(timezone=True), server_default=func.now())
	notes = Column(String(200), nullable=True)

	def __repr__(self):
		return f"<StatusHistory {self.order_id}: {self.old_status} -> {self.new_status}>"

	def to_dict(self):
		return {
			"history_id": self.history_id,
			"order_id": self.order_id,
			"old_status": self.old_status,
			"new_status": self.new_status,
			"changed_by": self.changed_by,
			"changed_at": str(self.changed_at),
			"notes": self.notes
		}

