"""Order Item Model - Individual items in an order"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey
from database.connection import Base


class OrderItem(Base):
	__tablename__ = "order_items"

	order_item_id = Column(Integer, primary_key=True, autoincrement=True)
	order_id = Column(String(20), ForeignKey("orders.order_id"), nullable=False, index=True)
	item_id = Column(Integer, ForeignKey("menu_items.item_id"), nullable=False)
	quantity = Column(Integer, nullable=False, default=1)
	item_price = Column(Float, nullable=False)
	subtotal = Column(Float, nullable=False)

	def __repr__(self):
		return f"<OrderItem {self.order_item_id} - Order:{self.order_id}>"

	def to_dict(self):
		return {
			"order_item_id": self.order_item_id,
			"order_id": self.order_id,
			"item_id": self.item_id,
			"quantity": self.quantity,
			"item_price": self.item_price,
			"subtotal": self.subtotal
		}

