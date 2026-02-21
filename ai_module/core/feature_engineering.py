"""
Feature Engineering Module
==========================
Extracts and transforms raw order data into features
that the ML model can understand and use for prediction.

This module handles:
- Time-based feature extraction (hour, day, peak hours)
- Item complexity calculation
- Load metrics computation (queue length, runner availability)
- Distance normalization
- Feature vector assembly for model input
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional


class FeatureEngineer:
	"""
	Transforms raw order data into ML-ready feature vectors.
    
	The model uses 11 features to predict ETA:
	1.  hour_of_day           - Hour when order was placed (0-23)
	2.  day_of_week           - Day of week (0=Monday, 6=Sunday)
	3.  active_orders_count   - Number of currently active orders
	4.  item_complexity       - Weighted complexity score of items
	5.  total_items           - Total number of items in order
	6.  available_runners     - Number of runners currently available
	7.  kitchen_queue_length  - Orders ahead in kitchen queue
	8.  avg_prep_time         - Average preparation time of ordered items
	9.  station_distance      - Distance from kitchen to station (meters)
	10. is_peak_hour          - Whether current time is peak hour (0 or 1)
	11. priority_encoded      - 0 for Regular, 1 for Urgent
	"""

	# Peak hours: Lunch (12-14) and Dinner (18-20)
	PEAK_HOUR_RANGES = [(12, 14), (18, 20)]

	# Maximum possible distance from kitchen to any station (meters)
	MAX_STATION_DISTANCE = 500

	# Feature names in exact order expected by model
	FEATURE_NAMES = [
		"hour_of_day",
		"day_of_week",
		"active_orders_count",
		"item_complexity",
		"total_items",
		"available_runners",
		"kitchen_queue_length",
		"avg_prep_time",
		"station_distance",
		"is_peak_hour",
		"priority_encoded",
	]

	def __init__(self):
		"""Initialize the Feature Engineer."""
		pass

	def extract_features(self, order_data: Dict[str, Any]) -> np.ndarray:
		"""
		Extract feature vector from raw order data.
        
		Args:
			order_data: Dictionary containing order information.
				Required keys:
				- items: List of dicts with 'prep_time', 'complexity_score', 'quantity'
				- station_distance: Distance in meters from kitchen
				- priority: 'Regular' or 'Urgent'
				- active_orders_count: Current active orders in system
				- available_runners: Currently available runners
				- kitchen_queue_length: Orders ahead in kitchen
				Optional keys:
				- order_time: datetime object (defaults to now)
        
		Returns:
			numpy array of shape (1, 11) ready for model prediction.
        
		Raises:
			ValueError: If required fields are missing or invalid.
		"""
		# Validate required fields exist
		self._validate_order_data(order_data)

		# Extract time features
		order_time = order_data.get("order_time", datetime.now())
		hour_of_day = self._extract_hour(order_time)
		day_of_week = self._extract_day_of_week(order_time)
		is_peak_hour = self._check_peak_hour(hour_of_day)

		# Extract item features
		items = order_data["items"]
		item_complexity = self._calculate_item_complexity(items)
		total_items = self._calculate_total_items(items)
		avg_prep_time = self._calculate_avg_prep_time(items)

		# Extract system load features
		active_orders_count = int(order_data["active_orders_count"])
		available_runners = int(order_data["available_runners"])
		kitchen_queue_length = int(order_data["kitchen_queue_length"])

		# Extract location feature
		station_distance = float(order_data["station_distance"])

		# Encode priority
		priority_encoded = self._encode_priority(order_data["priority"])

		# Assemble feature vector in correct order
		features = np.array([[
			hour_of_day,
			day_of_week,
			active_orders_count,
			item_complexity,
			total_items,
			available_runners,
			kitchen_queue_length,
			avg_prep_time,
			station_distance,
			is_peak_hour,
			priority_encoded,
		]])

		return features

	def extract_features_dataframe(
		self, order_data: Dict[str, Any]
	) -> pd.DataFrame:
		"""
		Extract features and return as a labeled DataFrame.
		Useful for debugging and logging.
        
		Args:
			order_data: Same as extract_features.
        
		Returns:
			pandas DataFrame with feature names as columns.
		"""
		features = self.extract_features(order_data)
		df = pd.DataFrame(features, columns=self.FEATURE_NAMES)
		return df

	def batch_extract_features(
		self, orders_data: List[Dict[str, Any]]
	) -> np.ndarray:
		"""
		Extract features for multiple orders at once.
        
		Args:
			orders_data: List of order data dictionaries.
        
		Returns:
			numpy array of shape (n_orders, 11).
		"""
		all_features = []
		for order_data in orders_data:
			features = self.extract_features(order_data)
			all_features.append(features[0])
		return np.array(all_features)

	# =============================================
	# Private Helper Methods
	# =============================================

	def _validate_order_data(self, order_data: Dict[str, Any]) -> None:
		"""
		Validate that all required fields are present in order data.
        
		Raises:
			ValueError: If any required field is missing or invalid.
		"""
		required_fields = [
			"items",
			"station_distance",
			"priority",
			"active_orders_count",
			"available_runners",
			"kitchen_queue_length",
		]

		for field in required_fields:
			if field not in order_data:
				raise ValueError(
					f"Missing required field: '{field}' in order data"
				)

		# Validate items is a non-empty list
		if not isinstance(order_data["items"], list):
			raise ValueError("'items' must be a list")
		if len(order_data["items"]) == 0:
			raise ValueError("'items' list cannot be empty")

		# Validate each item has required keys
		for i, item in enumerate(order_data["items"]):
			if "prep_time" not in item:
				raise ValueError(
					f"Item at index {i} missing 'prep_time'"
				)
			if "quantity" not in item:
				raise ValueError(
					f"Item at index {i} missing 'quantity'"
				)

		# Validate numeric fields are non-negative
		if float(order_data["station_distance"]) < 0:
			raise ValueError("'station_distance' cannot be negative")
		if int(order_data["active_orders_count"]) < 0:
			raise ValueError("'active_orders_count' cannot be negative")
		if int(order_data["available_runners"]) < 0:
			raise ValueError("'available_runners' cannot be negative")
		if int(order_data["kitchen_queue_length"]) < 0:
			raise ValueError("'kitchen_queue_length' cannot be negative")

		# Validate priority
		if order_data["priority"] not in ("Regular", "Urgent"):
			raise ValueError(
				"'priority' must be 'Regular' or 'Urgent'"
			)

	def _extract_hour(self, order_time: datetime) -> int:
		"""Extract hour from datetime (0-23)."""
		if isinstance(order_time, datetime):
			return order_time.hour
		return 12  # Default to noon if invalid

	def _extract_day_of_week(self, order_time: datetime) -> int:
		"""Extract day of week (0=Monday, 6=Sunday)."""
		if isinstance(order_time, datetime):
			return order_time.weekday()
		return 0  # Default to Monday if invalid

	def _check_peak_hour(self, hour: int) -> int:
		"""
		Check if given hour falls within peak hours.
		Peak hours: 12-14 (lunch), 18-20 (dinner).
        
		Returns:
			1 if peak hour, 0 otherwise.
		"""
		for start, end in self.PEAK_HOUR_RANGES:
			if start <= hour < end:
				return 1
		return 0

	def _calculate_item_complexity(
		self, items: List[Dict[str, Any]]
	) -> float:
		"""
		Calculate weighted complexity score for all items in order.
        
		Complexity is based on:
		- Each item's complexity_score (1=Simple, 2=Medium, 3=Complex)
		- Quantity of each item
        
		Formula: sum(complexity_score * quantity) for all items
        
		If complexity_score not provided, estimate from prep_time:
		- prep_time <= 5 min  → complexity 1 (Simple)
		- prep_time <= 12 min → complexity 2 (Medium)
		- prep_time > 12 min  → complexity 3 (Complex)
		"""
		total_complexity = 0.0
		for item in items:
			quantity = int(item.get("quantity", 1))

			if "complexity_score" in item:
				complexity = int(item["complexity_score"])
			else:
				# Estimate complexity from prep_time
				prep_time = float(item.get("prep_time", 5))
				if prep_time <= 5:
					complexity = 1
				elif prep_time <= 12:
					complexity = 2
				else:
					complexity = 3

			total_complexity += complexity * quantity

		return total_complexity

	def _calculate_total_items(
		self, items: List[Dict[str, Any]]
	) -> int:
		"""
		Calculate total number of items in the order.
		Counts each item's quantity.
		"""
		total = 0
		for item in items:
			total += int(item.get("quantity", 1))
		return total

	def _calculate_avg_prep_time(
		self, items: List[Dict[str, Any]]
	) -> float:
		"""
		Calculate average preparation time of items in the order.
		Weighted by quantity.
        
		Formula: sum(prep_time * quantity) / sum(quantity)
		"""
		total_prep = 0.0
		total_qty = 0

		for item in items:
			prep_time = float(item.get("prep_time", 5))
			quantity = int(item.get("quantity", 1))
			total_prep += prep_time * quantity
			total_qty += quantity

		if total_qty == 0:
			return 5.0  # Default prep time

		return round(total_prep / total_qty, 2)

	def _encode_priority(self, priority: str) -> int:
		"""
		Encode priority to numeric value.
		Regular = 0, Urgent = 1.
		"""
		if priority == "Urgent":
			return 1
		return 0

	def get_feature_summary(
		self, order_data: Dict[str, Any]
	) -> Dict[str, Any]:
		"""
		Get a human-readable summary of extracted features.
		Useful for API response and debugging.
        
		Returns:
			Dictionary with feature names and their values.
		"""
		features = self.extract_features(order_data)
		feature_values = features[0]

		summary = {}
		for name, value in zip(self.FEATURE_NAMES, feature_values):
			summary[name] = value

		# Add human-readable interpretations
		hour = int(summary["hour_of_day"])
		summary["time_description"] = f"{hour:02d}:00"

		days = [
			"Monday", "Tuesday", "Wednesday", "Thursday",
			"Friday", "Saturday", "Sunday"
		]
		day_idx = int(summary["day_of_week"])
		summary["day_description"] = days[day_idx]

		summary["is_peak_description"] = (
			"Yes" if summary["is_peak_hour"] == 1 else "No"
		)
		summary["priority_description"] = (
			"Urgent" if summary["priority_encoded"] == 1 else "Regular"
		)

		# Load assessment
		active = int(summary["active_orders_count"])
		if active <= 5:
			summary["kitchen_load"] = "Low"
		elif active <= 15:
			summary["kitchen_load"] = "Medium"
		else:
			summary["kitchen_load"] = "High"

		runners = int(summary["available_runners"])
		if runners >= 4:
			summary["runner_availability"] = "High"
		elif runners >= 2:
			summary["runner_availability"] = "Medium"
		else:
			summary["runner_availability"] = "Low"

		return summary
