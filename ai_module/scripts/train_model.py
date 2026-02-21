"""
Train ETA Prediction Model Script
=================================
Trains RandomForestRegressor on the generated training data.

Usage:
	python -m ai_module.scripts.train_model
	python -m ai_module.scripts.train_model --data ai_module/data/training_data.csv

Output:
	- ai_module/models/eta_model.pkl
	- ai_module/models/model_metadata.json
"""

import os
import sys
import argparse
import logging

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
	mean_absolute_error,
	mean_squared_error,
	r2_score,
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
	os.path.dirname(__file__), "..", ".."
)))

from ai_module.core.model_loader import ModelLoader

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def train_model(
	data_path: str = None,
	model_dir: str = None,
	test_size: float = 0.2,
	random_state: int = 42,
	n_estimators: int = 100,
) -> dict:
	"""
	Train ETA prediction model on historical data.
    
	Args:
		data_path: Path to training CSV file.
		model_dir: Directory to save trained model.
		test_size: Fraction of data for testing.
		random_state: Random seed.
		n_estimators: Number of trees in Random Forest.
    
	Returns:
		Dictionary with training metrics.
	"""
	# Default paths
	if data_path is None:
		data_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"data",
			"training_data.csv"
		)

	if model_dir is None:
		model_dir = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"models"
		)

	logger.info("=== Starting Model Training ===")
	logger.info(f"Loading data from: {data_path}")

	# Load data
	if not os.path.exists(data_path):
		raise FileNotFoundError(
			f"Training data not found at: {data_path}\n"
			f"Please run generate_data.py first."
		)

	df = pd.read_csv(data_path)
	logger.info(f"Loaded {len(df)} training records")

	# Define features and target
	feature_columns = [
		"hour_of_day",
		"day_of_week",
		"is_peak_hour",
		"is_weekend",
		"num_items",
		"item_complexity",
		"avg_prep_time",
		"station_distance",
		"active_orders_count",
		"kitchen_queue_length",
		"available_runners",
		"is_urgent",
	]
	target_column = "actual_eta_minutes"

	# Validate columns
	missing_cols = [
		col for col in feature_columns + [target_column]
		if col not in df.columns
	]
	if missing_cols:
		raise ValueError(
			f"Missing required columns in training data: {missing_cols}"
		)

	X = df[feature_columns]
	y = df[target_column]

	# Split data
	X_train, X_test, y_train, y_test = train_test_split(
		X,
		y,
		test_size=test_size,
		random_state=random_state,
	)

	logger.info(
		f"Train set: {len(X_train)} samples, "
		f"Test set: {len(X_test)} samples"
	)

	# Train model
	logger.info(
		f"Training RandomForestRegressor with {n_estimators} trees..."
	)
	model = RandomForestRegressor(
		n_estimators=n_estimators,
		max_depth=12,
		min_samples_split=5,
		min_samples_leaf=2,
		random_state=random_state,
		n_jobs=-1,
	)
	model.fit(X_train, y_train)

	# Evaluate
	y_pred = model.predict(X_test)
	mae = mean_absolute_error(y_test, y_pred)
	rmse = np.sqrt(mean_squared_error(y_test, y_pred))
	r2 = r2_score(y_test, y_pred)

	logger.info("\n=== Model Performance ===")
	logger.info(f"MAE  (Mean Absolute Error):  {mae:.3f} minutes")
	logger.info(f"RMSE (Root Mean Squared Error): {rmse:.3f} minutes")
	logger.info(f"R²   (R-squared Score):      {r2:.3f}")

	# Check threshold
	threshold_mae = 3.0
	if mae <= threshold_mae:
		logger.info(
			f"✅ Model meets production threshold "
			f"(MAE < {threshold_mae} min)"
		)
	else:
		logger.warning(
			f"⚠️ Model does NOT meet threshold "
			f"(MAE = {mae:.2f} > {threshold_mae} min)"
		)

	# Save model
	logger.info("\nSaving model...")
	success = ModelLoader.save_model(
		model=model,
		model_dir=model_dir,
		backup_existing=True,
	)

	if not success:
		raise RuntimeError("Failed to save trained model")

	# Save metadata
	ModelLoader.save_metadata(
		model_dir=model_dir,
		mae=mae,
		rmse=rmse,
		r2_score=r2,
		training_records=len(df),
		feature_names=feature_columns,
		model_type="RandomForestRegressor",
	)

	# Feature importance
	feature_importance = dict(
		zip(feature_columns, model.feature_importances_)
	)
	sorted_importance = sorted(
		feature_importance.items(),
		key=lambda x: x[1],
		reverse=True
	)

	logger.info("\n=== Top Feature Importance ===")
	for feature, importance in sorted_importance[:5]:
		logger.info(f"  {feature}: {importance:.3f}")

	metrics = {
		"mae": float(mae),
		"rmse": float(rmse),
		"r2_score": float(r2),
		"threshold_passed": bool(mae <= threshold_mae),
		"training_records": int(len(df)),
		"test_records": int(len(X_test)),
		"model_path": os.path.join(model_dir, "eta_model.pkl"),
	}

	logger.info("\n✅ Model training completed successfully!")
	return metrics


def main():
	"""CLI entry point."""
	parser = argparse.ArgumentParser(
		description="Train ETA prediction model"
	)
	parser.add_argument(
		"--data",
		type=str,
		default=None,
		help="Path to training data CSV"
	)
	parser.add_argument(
		"--model-dir",
		type=str,
		default=None,
		help="Directory to save trained model"
	)
	parser.add_argument(
		"--test-size",
		type=float,
		default=0.2,
		help="Test split ratio (default: 0.2)"
	)
	parser.add_argument(
		"--trees",
		type=int,
		default=100,
		help="Number of trees in Random Forest (default: 100)"
	)

	args = parser.parse_args()

	try:
		metrics = train_model(
			data_path=args.data,
			model_dir=args.model_dir,
			test_size=args.test_size,
			n_estimators=args.trees,
		)

		logger.info("\nTraining Summary:")
		logger.info(f"  MAE: {metrics['mae']:.3f} min")
		logger.info(f"  RMSE: {metrics['rmse']:.3f} min")
		logger.info(f"  R²: {metrics['r2_score']:.3f}")

	except Exception as e:
		logger.error(f"❌ Training failed: {str(e)}")
		sys.exit(1)


if __name__ == "__main__":
	main()
