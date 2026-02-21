"""AI Training Data Model - Data for AI model training"""

from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database.connection import Base


class AITrainingData(Base):
	__tablename__ = "ai_training_data"

	record_id = Column(Integer, primary_key=True, autoincrement=True)
	order_id = Column(String(20), ForeignKey("orders.order_id"), nullable=True)
	hour_of_day = Column(Integer, nullable=True)
	day_of_week = Column(Integer, nullable=True)
	active_orders_at_time = Column(Integer, nullable=True)
	item_complexity = Column(Integer, nullable=True)
	total_items = Column(Integer, nullable=True)
	available_runners = Column(Integer, nullable=True)
	kitchen_queue_length = Column(Integer, nullable=True)
	avg_prep_time = Column(Float, nullable=True)
	station_distance = Column(Integer, nullable=True)
	is_peak_hour = Column(Boolean, nullable=True)
	priority_encoded = Column(Integer, nullable=True)
	predicted_eta = Column(Integer, nullable=True)
	actual_delivery_minutes = Column(Integer, nullable=True)
	prediction_error = Column(Integer, nullable=True)
	recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

	def __repr__(self):
		return f"<AITrainingData {self.record_id} - Order:{self.order_id}>"

	def to_dict(self):
		return {
			"record_id": self.record_id,
			"order_id": self.order_id,
			"hour_of_day": self.hour_of_day,
			"day_of_week": self.day_of_week,
			"active_orders_at_time": self.active_orders_at_time,
			"item_complexity": self.item_complexity,
			"total_items": self.total_items,
			"available_runners": self.available_runners,
			"kitchen_queue_length": self.kitchen_queue_length,
			"avg_prep_time": self.avg_prep_time,
			"station_distance": self.station_distance,
			"is_peak_hour": self.is_peak_hour,
			"priority_encoded": self.priority_encoded,
			"predicted_eta": self.predicted_eta,
			"actual_delivery_minutes": self.actual_delivery_minutes,
			"prediction_error": self.prediction_error,
			"recorded_at": str(self.recorded_at)
		}

