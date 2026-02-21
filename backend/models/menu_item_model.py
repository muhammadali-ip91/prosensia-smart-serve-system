"""Menu Item Model - Food items available for ordering"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func
from database.connection import Base


class MenuItem(Base):
	__tablename__ = "menu_items"

	item_id = Column(Integer, primary_key=True, autoincrement=True)
	item_name = Column(String(100), nullable=False)
	category = Column(String(50), nullable=False, index=True)
	price = Column(Float, nullable=False)
	prep_time_estimate = Column(Integer, nullable=False)
	complexity_score = Column(Integer, default=1)
	image_url = Column(String(500), nullable=True)
	is_available = Column(Boolean, default=True, index=True)
	unavailable_reason = Column(String(200), nullable=True)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	def __repr__(self):
		return f"<MenuItem {self.item_id} - {self.item_name}>"

	def to_dict(self):
		return {
			"item_id": self.item_id,
			"item_name": self.item_name,
			"category": self.category,
			"price": self.price,
			"prep_time_estimate": self.prep_time_estimate,
			"complexity_score": self.complexity_score,
			"image_url": self.image_url,
			"is_available": self.is_available,
			"unavailable_reason": self.unavailable_reason
		}

