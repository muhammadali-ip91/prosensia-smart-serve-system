"""
Fallback Prediction Module
==========================
Provides ETA predictions when the AI model is unavailable.

This module is used when:
- Model file is missing or corrupted
- Model fails to load
- Model prediction throws an exception
- Model is being retrained

The fallback uses simple rule-based logic based on:
- Average preparation time of items
- Number of items in order
- Kitchen queue length
- Runner availability
- Station distance
- Peak hour adjustment

It's designed to NEVER fail — always returns a reasonable ETA.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class FallbackPredictor:
	"""
	Rule-based ETA predictor used as fallback when AI model
	is unavailable.
    
	This ensures the engineer ALWAYS sees an ETA estimate,
	even if the ML model crashes.
	"""

	# Base delivery time (runner walking time) in minutes
	BASE_DELIVERY_TIME = 3.0

	# Time per meter of distance (minutes per meter)
	DISTANCE_FACTOR = 0.02

	# Additional time per order ahead in queue (minutes)
	QUEUE_FACTOR = 1.5

	# Peak hour multiplier (adds percentage to total ETA)
	PEAK_HOUR_MULTIPLIER = 1.3

	# Urgent order discount (reduces ETA by percentage)
	URGENT_DISCOUNT = 0.85

	# Minimum ETA (never predict less than this)
	MIN_ETA_MINUTES = 3

	# Maximum ETA (never predict more than this)
	MAX_ETA_MINUTES = 60

	# Runner shortage penalty (when few runners available)
	LOW_RUNNER_PENALTY = 5.0  # Extra minutes when runners < 2

	def __init__(self):
		"""Initialize the Fallback Predictor."""
		logger.info("FallbackPredictor initialized.")

	def predict(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Generate a rule-based ETA prediction.
        
		Args:
			order_data: Dictionary with order information.
				Required keys:
				- items: List of dicts with 'prep_time' and 'quantity'
				- station_distance: Distance in meters
				- priority: 'Regular' or 'Urgent'
				- kitchen_queue_length: Orders ahead in queue
				- available_runners: Available runners count
				Optional keys:
				- is_peak_hour: Boolean or int (0/1)
        
		Returns:
			Dictionary with:
			- predicted_eta_minutes: int
			- confidence_score: float (always lower than ML model)
			- source: "fallback"
			- factors: dict with factor descriptions
		"""
		try:
			# Step 1: Calculate base preparation time
			prep_time = self._calculate_prep_time(
				order_data.get("items", [])
			)

			# Step 2: Calculate queue wait time
			queue_length = int(
				order_data.get("kitchen_queue_length", 0)
			)
			queue_time = queue_length * self.QUEUE_FACTOR

			# Step 3: Calculate delivery time based on distance
			distance = float(
				order_data.get("station_distance", 100)
			)
			delivery_time = (
				self.BASE_DELIVERY_TIME
				+ distance * self.DISTANCE_FACTOR
			)

			# Step 4: Calculate runner penalty
			available_runners = int(
				order_data.get("available_runners", 3)
			)
			runner_penalty = 0.0
			if available_runners < 2:
				runner_penalty = self.LOW_RUNNER_PENALTY
			elif available_runners < 3:
				runner_penalty = self.LOW_RUNNER_PENALTY / 2

			# Step 5: Sum up total time
			total_eta = (
				prep_time + queue_time + delivery_time + runner_penalty
			)

			# Step 6: Apply peak hour multiplier
			is_peak = order_data.get("is_peak_hour", 0)
			if isinstance(is_peak, bool):
				is_peak = 1 if is_peak else 0
			if is_peak:
				total_eta *= self.PEAK_HOUR_MULTIPLIER

			# Step 7: Apply urgent discount
			priority = order_data.get("priority", "Regular")
			if priority == "Urgent":
				total_eta *= self.URGENT_DISCOUNT

			# Step 8: Clamp to min/max range
			total_eta = max(
				self.MIN_ETA_MINUTES,
				min(self.MAX_ETA_MINUTES, total_eta)
			)

			# Round to nearest integer
			predicted_eta = round(total_eta)

			# Determine factor descriptions
			factors = self._get_factor_descriptions(
				queue_length, available_runners, is_peak, priority
			)

			logger.info(
				f"Fallback prediction: {predicted_eta} minutes "
				f"(prep={prep_time:.1f}, queue={queue_time:.1f}, "
				f"delivery={delivery_time:.1f}, "
				f"runner_penalty={runner_penalty:.1f})"
			)

			return {
				"predicted_eta_minutes": predicted_eta,
				"confidence_score": 0.55,  # Lower than ML model
				"source": "fallback",
				"factors": factors,
				"breakdown": {
					"prep_time": round(prep_time, 1),
					"queue_wait": round(queue_time, 1),
					"delivery_time": round(delivery_time, 1),
					"runner_penalty": round(runner_penalty, 1),
					"peak_multiplier_applied": bool(is_peak),
					"urgent_discount_applied": (
						priority == "Urgent"
					),
				},
			}

		except Exception as e:
			# ULTIMATE FALLBACK: If even the fallback calculation
			# fails, return a safe default
			logger.error(
				f"Fallback prediction failed: {str(e)}. "
				f"Using ultimate default."
			)
			return {
				"predicted_eta_minutes": 15,
				"confidence_score": 0.3,
				"source": "fallback_default",
				"factors": {
					"kitchen_load": "Unknown",
					"runner_availability": "Unknown",
					"item_complexity": "Unknown",
				},
				"breakdown": {
					"note": "Default estimate due to calculation error"
				},
			}

	def _calculate_prep_time(self, items: list) -> float:
		"""
		Calculate total preparation time for all items.
        
		Logic: Takes the MAXIMUM prep time across all items
		(since kitchen prepares items in parallel),
		plus a small addition for each extra item type.
        
		Example:
		- Biryani (15 min) + Chai (3 min) + Samosa (5 min)
		- Max = 15 min
		- Extra items = 2 items × 1 min = 2 min
		- Total = 17 min (not 23 min, because parallel prep)
		"""
		if not items:
			return 5.0  # Default if no items info

		prep_times = []
		for item in items:
			prep_time = float(item.get("prep_time", 5))
			quantity = int(item.get("quantity", 1))
			# Additional time for quantity > 1
			# (2 biryanis take slightly longer than 1)
			adjusted_prep = prep_time + (quantity - 1) * 1.5
			prep_times.append(adjusted_prep)

		if not prep_times:
			return 5.0

		# Max prep time (parallel preparation)
		max_prep = max(prep_times)

		# Small addition for each extra item type
		extra_items = len(prep_times) - 1
		extra_time = extra_items * 1.0

		return max_prep + extra_time

	def _get_factor_descriptions(
		self,
		queue_length: int,
		available_runners: int,
		is_peak: int,
		priority: str,
	) -> Dict[str, str]:
		"""Generate human-readable factor descriptions."""
		# Kitchen load
		if queue_length <= 3:
			kitchen_load = "Low"
		elif queue_length <= 10:
			kitchen_load = "Medium"
		else:
			kitchen_load = "High"

		# Runner availability
		if available_runners >= 4:
			runner_avail = "High"
		elif available_runners >= 2:
			runner_avail = "Medium"
		else:
			runner_avail = "Low"

		return {
			"kitchen_load": kitchen_load,
			"runner_availability": runner_avail,
			"peak_hour": "Yes" if is_peak else "No",
			"priority": priority,
		}
