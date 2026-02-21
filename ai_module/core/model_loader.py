"""
Model Loader Module
===================
Safely loads the trained ML model from disk with comprehensive
error handling. If the model file is missing, corrupted, or
incompatible, the loader returns None and the system falls
back to the FallbackPredictor.

This module handles:
- Loading model from .pkl file using joblib
- Loading model metadata (accuracy, training date)
- Model version management
- Safe error handling (never crashes the system)
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

import joblib

logger = logging.getLogger(__name__)


class ModelLoader:
	"""
	Safely loads and manages the ETA prediction model.
    
	The loader looks for model files in a specified directory
	and handles all possible failure scenarios gracefully.
	"""

	# Default paths relative to ai_module directory
	DEFAULT_MODEL_DIR = os.path.join(
		os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
		"models"
	)
	DEFAULT_MODEL_FILENAME = "eta_model.pkl"
	DEFAULT_BACKUP_FILENAME = "eta_model_backup.pkl"
	DEFAULT_METADATA_FILENAME = "model_metadata.json"

	def __init__(self, model_dir: Optional[str] = None):
		"""
		Initialize the model loader.
        
		Args:
			model_dir: Directory containing model files.
					   Defaults to ai_module/models/
		"""
		self.model_dir = model_dir or self.DEFAULT_MODEL_DIR
		self.model_path = os.path.join(
			self.model_dir, self.DEFAULT_MODEL_FILENAME
		)
		self.backup_path = os.path.join(
			self.model_dir, self.DEFAULT_BACKUP_FILENAME
		)
		self.metadata_path = os.path.join(
			self.model_dir, self.DEFAULT_METADATA_FILENAME
		)

		self._model = None
		self._metadata = None
		self._is_loaded = False
		self._load_source = None  # 'primary', 'backup', or None

	def load_model(self) -> Optional[Any]:
		"""
		Load the trained model from disk.
        
		Attempts to load the primary model first.
		If that fails, tries the backup model.
		If both fail, returns None (system will use fallback).
        
		Returns:
			Loaded sklearn model, or None if loading failed.
		"""
		# Attempt 1: Load primary model
		model = self._try_load_model(self.model_path, "primary")
		if model is not None:
			self._model = model
			self._is_loaded = True
			self._load_source = "primary"
			self._metadata = self._load_metadata()
			logger.info(
				f"AI Model loaded successfully from primary: "
				f"{self.model_path}"
			)
			return model

		# Attempt 2: Load backup model
		logger.warning(
			"Primary model failed to load. Trying backup model..."
		)
		model = self._try_load_model(self.backup_path, "backup")
		if model is not None:
			self._model = model
			self._is_loaded = True
			self._load_source = "backup"
			self._metadata = self._load_metadata()
			logger.warning(
				f"AI Model loaded from BACKUP: {self.backup_path}"
			)
			return model

		# Both failed
		logger.error(
			"CRITICAL: Both primary and backup models failed to load. "
			"System will use fallback prediction."
		)
		self._model = None
		self._is_loaded = False
		self._load_source = None
		return None

	def _try_load_model(
		self, path: str, source_name: str
	) -> Optional[Any]:
		"""
		Attempt to load a model from a specific path.
        
		Args:
			path: Path to the model file.
			source_name: Name for logging ('primary' or 'backup').
        
		Returns:
			Loaded model or None if failed.
		"""
		try:
			# Check if file exists
			if not os.path.exists(path):
				logger.warning(
					f"Model file not found at: {path}"
				)
				return None

			# Check if file is not empty
			if os.path.getsize(path) == 0:
				logger.warning(
					f"Model file is empty: {path}"
				)
				return None

			# Load the model
			model = joblib.load(path)

			# Verify model has predict method
			if not hasattr(model, "predict"):
				logger.error(
					f"Loaded object from {source_name} does not have "
					f"'predict' method. Not a valid model."
				)
				return None

			logger.info(
				f"Model loaded from {source_name}: {path}"
			)
			return model

		except Exception as e:
			logger.error(
				f"Error loading {source_name} model from {path}: "
				f"{type(e).__name__}: {str(e)}"
			)
			return None

	def _load_metadata(self) -> Optional[Dict[str, Any]]:
		"""
		Load model metadata from JSON file.
        
		Returns:
			Dictionary with model metadata, or None if not found.
		"""
		try:
			if not os.path.exists(self.metadata_path):
				logger.info("No model metadata file found.")
				return None

			with open(self.metadata_path, "r") as f:
				metadata = json.load(f)

			logger.info(
				f"Model metadata loaded: "
				f"trained_at={metadata.get('trained_at', 'unknown')}, "
				f"mae={metadata.get('mae', 'unknown')}"
			)
			return metadata

		except Exception as e:
			logger.warning(
				f"Could not load model metadata: {str(e)}"
			)
			return None

	@staticmethod
	def save_metadata(
		model_dir: str,
		mae: float,
		rmse: float,
		r2_score: float,
		training_records: int,
		feature_names: list,
		model_type: str = "RandomForestRegressor",
	) -> None:
		"""
		Save model metadata to JSON file after training.
        
		Args:
			model_dir: Directory to save metadata.
			mae: Mean Absolute Error of the model.
			rmse: Root Mean Squared Error of the model.
			r2_score: R-squared score of the model.
			training_records: Number of records used for training.
			feature_names: List of feature names used.
			model_type: Type of ML algorithm used.
		"""
		metadata = {
			"model_type": model_type,
			"trained_at": datetime.now().isoformat(),
			"metrics": {
				"mae": round(mae, 4),
				"rmse": round(rmse, 4),
				"r2_score": round(r2_score, 4),
			},
			"training_records": training_records,
			"feature_names": feature_names,
			"version": datetime.now().strftime("%Y%m%d_%H%M%S"),
			"threshold_mae": 3.0,
			"passed_threshold": mae < 3.0,
		}

		metadata_path = os.path.join(
			model_dir, "model_metadata.json"
		)

		try:
			os.makedirs(model_dir, exist_ok=True)
			with open(metadata_path, "w") as f:
				json.dump(metadata, f, indent=2)
			logger.info(
				f"Model metadata saved to: {metadata_path}"
			)
		except Exception as e:
			logger.error(
				f"Failed to save model metadata: {str(e)}"
			)

	@staticmethod
	def save_model(
		model: Any,
		model_dir: str,
		backup_existing: bool = True,
	) -> bool:
		"""
		Save a trained model to disk.
		If backup_existing is True, copies current model to backup first.
        
		Args:
			model: Trained sklearn model to save.
			model_dir: Directory to save model.
			backup_existing: Whether to backup the current model first.
        
		Returns:
			True if saved successfully, False otherwise.
		"""
		model_path = os.path.join(model_dir, "eta_model.pkl")
		backup_path = os.path.join(model_dir, "eta_model_backup.pkl")

		try:
			os.makedirs(model_dir, exist_ok=True)

			# Backup existing model if requested
			if backup_existing and os.path.exists(model_path):
				try:
					import shutil
					shutil.copy2(model_path, backup_path)
					logger.info(
						f"Existing model backed up to: {backup_path}"
					)
				except Exception as backup_error:
					logger.warning(
						f"Could not backup existing model: "
						f"{str(backup_error)}"
					)

			# Save new model
			joblib.dump(model, model_path)
			logger.info(
				f"Model saved successfully to: {model_path}"
			)
			return True

		except Exception as e:
			logger.error(
				f"Failed to save model: {str(e)}"
			)
			return False

	# =============================================
	# Properties
	# =============================================

	@property
	def model(self) -> Optional[Any]:
		"""Get the loaded model."""
		return self._model

	@property
	def is_loaded(self) -> bool:
		"""Check if model is successfully loaded."""
		return self._is_loaded

	@property
	def load_source(self) -> Optional[str]:
		"""Get the source from which model was loaded."""
		return self._load_source

	@property
	def metadata(self) -> Optional[Dict[str, Any]]:
		"""Get model metadata."""
		return self._metadata

	def get_model_info(self) -> Dict[str, Any]:
		"""
		Get comprehensive information about the loaded model.
		Useful for health checks and admin dashboard.
        
		Returns:
			Dictionary with model status information.
		"""
		info = {
			"is_loaded": self._is_loaded,
			"load_source": self._load_source,
			"model_path": self.model_path,
			"model_file_exists": os.path.exists(self.model_path),
			"backup_file_exists": os.path.exists(self.backup_path),
		}

		if self._metadata:
			info["trained_at"] = self._metadata.get("trained_at")
			info["metrics"] = self._metadata.get("metrics")
			info["version"] = self._metadata.get("version")
			info["training_records"] = self._metadata.get(
				"training_records"
			)
			info["passed_threshold"] = self._metadata.get(
				"passed_threshold"
			)
		else:
			info["trained_at"] = None
			info["metrics"] = None
			info["version"] = None

		return info
