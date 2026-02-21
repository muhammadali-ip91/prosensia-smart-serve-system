"""
ETA Predictor Module
====================
Main prediction engine that combines ML model with fallback logic.

This is the PRIMARY INTERFACE that the backend calls.
It handles:
- Loading the model (via ModelLoader)
- Extracting features (via FeatureEngineer)
- Making predictions (via loaded model)
- Falling back gracefully (via FallbackPredictor)
- Returning structured prediction results
- Logging prediction accuracy for monitoring

Usage from backend:
	from ai_module.core.predictor import ETAPredictor
    
	predictor = ETAPredictor()
	result = predictor.predict(order_data)
	# result = {
	#     "predicted_eta_minutes": 14,
	#     "confidence_score": 0.85,
	#     "source": "ai_model",
	#     "factors": {...}
	# }
"""

import logging
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime

from ai_module.core.model_loader import ModelLoader
from ai_module.core.feature_engineering import FeatureEngineer
from ai_module.core.fallback import FallbackPredictor

logger = logging.getLogger(__name__)


class ETAPredictor:
	"""
	Main ETA prediction class.
    
	This class is the single entry point for all ETA predictions
	in the system. It automatically:
	1. Tries to use the trained ML model
	2. Falls back to rule-based prediction if model unavailable
	3. Uses ultimate default (15 min) if everything fails
    
	The engineer NEVER sees a blank ETA — guaranteed.
	"""

	# Minimum and maximum ETA bounds
	MIN_ETA = 3    # minutes
	MAX_ETA = 60   # minutes

	# Confidence thresholds
	HIGH_CONFIDENCE = 0.85
	MEDIUM_CONFIDENCE = 0.70
	LOW_CONFIDENCE = 0.55

	def __init__(self, model_dir: Optional[str] = None):
		"""
		Initialize the ETA Predictor.
        
		Loads the ML model and initializes feature engineering
		and fallback components.
        
		Args:
			model_dir: Directory containing model files.
					   Defaults to ai_module/models/
		"""
		logger.info("Initializing ETAPredictor...")

		# Initialize components
		self.feature_engineer = FeatureEngineer()
		self.fallback_predictor = FallbackPredictor()
		self.model_loader = ModelLoader(model_dir=model_dir)

		# Load the model
		self.model = self.model_loader.load_model()

		if self.model is not None:
			logger.info(
				"ETAPredictor ready with AI model "
				f"(source: {self.model_loader.load_source})"
			)
		else:
			logger.warning(
				"ETAPredictor ready in FALLBACK MODE "
				"(no AI model loaded)"
			)

		# Prediction counter for monitoring
		self._total_predictions = 0
		self._model_predictions = 0
		self._fallback_predictions = 0

	def predict(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Predict ETA for a given order.
        
		This is the MAIN METHOD called by the backend.
        
		Args:
			order_data: Dictionary containing order information.
				Required keys:
				- items: List of dicts with 'prep_time',
						 'complexity_score', 'quantity'
				- station_distance: Distance in meters
				- priority: 'Regular' or 'Urgent'
				- active_orders_count: Currently active orders
				- available_runners: Available runner count
				- kitchen_queue_length: Orders ahead in queue
				Optional keys:
				- order_time: datetime object
        
		Returns:
			Dictionary with:
			- predicted_eta_minutes: int (the prediction)
			- confidence_score: float (0.0 to 1.0)
			- source: str ("ai_model" or "fallback")
			- factors: dict (human-readable factors)
			- feature_summary: dict (extracted features, optional)
		"""
		self._total_predictions += 1

		# Attempt 1: Use AI Model
		if self.model is not None:
			try:
				result = self._predict_with_model(order_data)
				self._model_predictions += 1
				logger.info(
					f"AI Model prediction: "
					f"{result['predicted_eta_minutes']} min "
					f"(confidence: {result['confidence_score']:.2f})"
				)
				return result

			except Exception as e:
				logger.error(
					f"AI Model prediction failed: "
					f"{type(e).__name__}: {str(e)}. "
					f"Falling back to rule-based prediction."
				)

		# Attempt 2: Use Fallback
		try:
			result = self.fallback_predictor.predict(order_data)
			self._fallback_predictions += 1
			logger.info(
				f"Fallback prediction: "
				f"{result['predicted_eta_minutes']} min"
			)
			return result

		except Exception as e:
			# Attempt 3: Ultimate fallback (should NEVER reach here)
			logger.critical(
				f"BOTH AI model and fallback failed: {str(e)}. "
				f"Using ultimate default."
			)
			self._fallback_predictions += 1
			return {
				"predicted_eta_minutes": 15,
				"confidence_score": 0.3,
				"source": "ultimate_fallback",
				"factors": {
					"kitchen_load": "Unknown",
					"runner_availability": "Unknown",
					"item_complexity": "Unknown",
				},
			}

	def _predict_with_model(
		self, order_data: Dict[str, Any]
	) -> Dict[str, Any]:
		"""
		Make prediction using the trained ML model.
        
		Steps:
		1. Extract features from order data
		2. Feed features to model
		3. Post-process prediction (clamp, round)
		4. Calculate confidence score
		5. Generate factor descriptions
        
		Args:
			order_data: Raw order data dictionary.
        
		Returns:
			Structured prediction result.
        
		Raises:
			Exception: If feature extraction or model prediction fails.
		"""
		# Step 1: Extract features
		features = self.feature_engineer.extract_features(order_data)

		# Step 2: Get feature summary for response
		feature_summary = self.feature_engineer.get_feature_summary(
			order_data
		)

		# Step 3: Make prediction
		raw_prediction = self.model.predict(features)[0]

		# Step 4: Post-process
		# Clamp prediction to valid range
		predicted_eta = max(
			self.MIN_ETA,
			min(self.MAX_ETA, raw_prediction)
		)
		predicted_eta = round(predicted_eta)

		# Step 5: Calculate confidence score
		confidence = self._calculate_confidence(
			order_data, predicted_eta
		)

		# Step 6: Generate factors description
		factors = self._generate_factors(feature_summary)

		return {
			"predicted_eta_minutes": predicted_eta,
			"confidence_score": round(confidence, 2),
			"source": "ai_model",
			"model_source": self.model_loader.load_source,
			"factors": factors,
			"feature_summary": feature_summary,
			"raw_prediction": round(float(raw_prediction), 2),
		}

	def _calculate_confidence(
		self,
		order_data: Dict[str, Any],
		predicted_eta: int,
	) -> float:
		"""
		Calculate confidence score for the prediction.
        
		Confidence is higher when:
		- System load is moderate (not extreme)
		- Sufficient runners are available
		- Not during unusual hours
		- Model has metadata showing good accuracy
        
		Returns:
			Float between 0.0 and 1.0
		"""
		base_confidence = 0.80

		# Factor 1: Runner availability
		runners = int(order_data.get("available_runners", 3))
		if runners >= 3:
			base_confidence += 0.05
		elif runners == 0:
			base_confidence -= 0.15
		elif runners == 1:
			base_confidence -= 0.10

		# Factor 2: Kitchen queue (very long queues = less certain)
		queue = int(order_data.get("kitchen_queue_length", 0))
		if queue > 20:
			base_confidence -= 0.10
		elif queue > 10:
			base_confidence -= 0.05

		# Factor 3: Active orders (extreme load = less certain)
		active = int(order_data.get("active_orders_count", 0))
		if active > 30:
			base_confidence -= 0.10
		elif active > 15:
			base_confidence -= 0.05

		# Factor 4: Model metadata (if available)
		if self.model_loader.metadata:
			metrics = self.model_loader.metadata.get("metrics", {})
			mae = metrics.get("mae", 3.0)
			if mae < 2.0:
				base_confidence += 0.05
			elif mae > 4.0:
				base_confidence -= 0.10

		# Clamp confidence to valid range
		return max(0.30, min(0.95, base_confidence))

	def _generate_factors(
		self, feature_summary: Dict[str, Any]
	) -> Dict[str, str]:
		"""
		Generate human-readable factor descriptions for API response.
		"""
		return {
			"kitchen_load": feature_summary.get(
				"kitchen_load", "Unknown"
			),
			"runner_availability": feature_summary.get(
				"runner_availability", "Unknown"
			),
			"peak_hour": feature_summary.get(
				"is_peak_description", "No"
			),
			"item_complexity": self._describe_complexity(
				feature_summary.get("item_complexity", 1)
			),
		}

	@staticmethod
	def _describe_complexity(complexity: float) -> str:
		"""Convert numeric complexity to description."""
		if complexity <= 2:
			return "Low"
		elif complexity <= 5:
			return "Medium"
		else:
			return "High"

	def reload_model(self) -> bool:
		"""
		Reload the model from disk.
		Useful after retraining without restarting the server.
        
		Returns:
			True if model loaded successfully, False otherwise.
		"""
		logger.info("Reloading AI model...")
		self.model = self.model_loader.load_model()

		if self.model is not None:
			logger.info("Model reloaded successfully.")
			return True
		else:
			logger.warning(
				"Model reload failed. Continuing with fallback."
			)
			return False

	def get_stats(self) -> Dict[str, Any]:
		"""
		Get prediction statistics for monitoring.
		Useful for admin dashboard and health checks.
		"""
		model_info = self.model_loader.get_model_info()

		return {
			"total_predictions": self._total_predictions,
			"model_predictions": self._model_predictions,
			"fallback_predictions": self._fallback_predictions,
			"model_usage_rate": (
				round(
					self._model_predictions / self._total_predictions,
					2
				)
				if self._total_predictions > 0
				else 0.0
			),
			"model_info": model_info,
			"is_model_active": self.model is not None,
		}
