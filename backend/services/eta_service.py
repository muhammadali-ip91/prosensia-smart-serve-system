"""AI ETA Prediction Service"""

import joblib
import numpy as np
import os
import json
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger
from datetime import datetime

from config import settings
from utils.time_utils import is_peak_hour, get_current_hour, get_current_day_of_week
from utils.constants import OrderStatus
from models.order_model import Order
from models.runner_model import Runner
from models.station_model import Station
from models.ai_training_data_model import AITrainingData


class ETAService:
	"""AI-powered ETA prediction service"""

	def __init__(self):
		self.model = None
		self.metadata = None
		self.model_loaded = False

	def load_model(self):
		"""Load the trained model"""
		configured_model_path = settings.AI_MODEL_PATH
		backend_dir = os.path.dirname(os.path.dirname(__file__))
		project_root = os.path.dirname(backend_dir)

		candidate_model_paths = [
			configured_model_path,
			os.path.join(project_root, configured_model_path),
		]

		model_path = next((p for p in candidate_model_paths if os.path.exists(p)), configured_model_path)
		metadata_path = model_path.replace(".pkl", "_metadata.json")

		# Alternative metadata path
		alt_metadata_path = os.path.join(
			os.path.dirname(model_path), "model_metadata.json"
		)

		try:
			if os.path.exists(model_path):
				self.model = joblib.load(model_path)
				self.model_loaded = True
				logger.info(f"✅ AI Model loaded from {model_path}")

				# Load metadata
				for meta_path in [metadata_path, alt_metadata_path]:
					if os.path.exists(meta_path):
						with open(meta_path, 'r') as f:
							self.metadata = json.load(f)
						break
			else:
				logger.warning(f"⚠️ Model not found at {model_path}")
				self.model_loaded = False

		except Exception as e:
			logger.error(f"❌ Failed to load AI model: {e}")
			self.model_loaded = False

	def predict(self, db: Session, station_id: str, items: list,
				priority: str) -> dict:
		"""Predict delivery ETA"""

		# Gather system state
		active_orders = db.query(Order).filter(
			Order.status.in_(OrderStatus.ACTIVE)
		).count()

		available_runners = db.query(Runner).filter(
			Runner.current_status == "Available"
		).count()

		kitchen_queue = db.query(Order).filter(
			Order.status.in_([OrderStatus.PLACED, OrderStatus.CONFIRMED])
		).count()

		# Station distance
		station = db.query(Station).filter(
			Station.station_id == station_id
		).first()
		station_distance = station.distance_from_kitchen if station else 200

		# Item details
		total_items = sum(item["quantity"] for item in items)
		max_complexity = max(
			item.get("menu_item", {}).complexity_score
			if hasattr(item.get("menu_item", {}), "complexity_score")
			else 2
			for item in items
		) if items else 2

		avg_prep_time = sum(
			item.get("menu_item", {}).prep_time_estimate
			if hasattr(item.get("menu_item", {}), "prep_time_estimate")
			else 10
			for item in items
		) / max(len(items), 1) if items else 10

		peak = is_peak_hour()
		priority_encoded = 1 if priority == "Urgent" else 0

		# Try AI prediction
		if self.model_loaded:
			try:
				features = np.array([[
					get_current_hour(),
					get_current_day_of_week(),
					active_orders,
					max_complexity,
					total_items,
					available_runners,
					kitchen_queue,
					avg_prep_time,
					station_distance,
					1 if peak else 0,
					priority_encoded
				]])

				predicted_eta = self.model.predict(features)[0]
				predicted_eta = max(3, min(60, round(predicted_eta, 1)))

				confidence = 0.85
				if self.metadata and "metrics" in self.metadata:
					r2 = self.metadata["metrics"].get("r2_score", 0.85)
					confidence = min(0.95, max(0.5, r2))

				return {
					"predicted_eta_minutes": predicted_eta,
					"confidence_score": round(confidence, 2),
					"source": "ai_model",
					"factors": self._analyze_factors(
						active_orders, available_runners,
						kitchen_queue, peak, max_complexity
					)
				}

			except Exception as e:
				logger.warning(f"AI prediction failed: {e}, using fallback")

		# Fallback prediction
		return self._fallback_prediction(
			avg_prep_time, station_distance, active_orders,
			available_runners, peak, priority_encoded
		)

	def _fallback_prediction(self, avg_prep_time, station_distance,
							  active_orders, available_runners,
							  is_peak, priority):
		"""Simple formula-based fallback"""
		eta = (
			avg_prep_time
			+ (station_distance / 80)
			+ (active_orders * 0.4)
			- (max(available_runners, 1) * 0.5)
			+ (is_peak * 5)
			- (priority * 2)
		)
		eta = max(3, min(60, round(eta, 1)))

		return {
			"predicted_eta_minutes": eta,
			"confidence_score": 0.60,
			"source": "fallback",
			"factors": {
				"kitchen_load": "Unknown",
				"runner_availability": "Unknown",
				"item_complexity": "Unknown",
				"note": "AI model unavailable. Using simple calculation."
			}
		}

	def _analyze_factors(self, active_orders, available_runners,
						  kitchen_queue, is_peak, complexity):
		"""Analyze contributing factors"""
		return {
			"kitchen_load": "High" if kitchen_queue > 15 else
						   "Medium" if kitchen_queue > 8 else "Low",
			"runner_availability": "Low" if available_runners <= 1 else
								  "Medium" if available_runners <= 3 else "High",
			"item_complexity": {1: "Low", 2: "Medium", 3: "High"}.get(complexity, "Medium"),
			"is_peak_hour": bool(is_peak),
			"active_orders": active_orders
		}


def log_training_data(db: Session, order: Order):
	"""Log delivered order data for AI training"""
	try:
		active_at_time = db.query(Order).filter(
			Order.created_at <= order.created_at,
			Order.status.in_(OrderStatus.ACTIVE)
		).count()

		runners_at_time = db.query(Runner).filter(
			Runner.current_status == "Available"
		).count()

		station = db.query(Station).filter(
			Station.station_id == order.station_id
		).first()

		training_record = AITrainingData(
			order_id=order.order_id,
			hour_of_day=order.created_at.hour,
			day_of_week=order.created_at.weekday(),
			active_orders_at_time=active_at_time,
			available_runners=runners_at_time,
			station_distance=station.distance_from_kitchen if station else 200,
			is_peak_hour=is_peak_hour(order.created_at.hour),
			priority_encoded=1 if order.priority == "Urgent" else 0,
			predicted_eta=order.ai_predicted_eta,
			actual_delivery_minutes=order.actual_delivery_time,
			prediction_error=abs(
				(order.ai_predicted_eta or 0) - (order.actual_delivery_time or 0)
			)
		)
		db.add(training_record)
		db.flush()

		logger.info(f"AI training data logged for order {order.order_id}")

	except Exception as e:
		logger.error(f"Failed to log AI training data: {e}")


# Global service instance
eta_service = ETAService()

