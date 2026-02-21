"""Kitchen Settings Model - global kitchen status and working hours"""

from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func

from database.connection import Base


class KitchenSettings(Base):
	__tablename__ = "kitchen_settings"

	id = Column(Integer, primary_key=True, default=1)
	force_closed = Column(Boolean, default=False, nullable=False)
	open_hour = Column(Integer, default=9, nullable=False)
	close_hour = Column(Integer, default=21, nullable=False)
	updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	def to_dict(self):
		return {
			"force_closed": self.force_closed,
			"open_hour": self.open_hour,
			"close_hour": self.close_hour,
		}
