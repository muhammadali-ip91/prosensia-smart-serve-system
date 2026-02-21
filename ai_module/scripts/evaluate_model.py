"""
Evaluate ETA Prediction Model Script
====================================
Evaluates trained model performance on test data.

Usage:
	python -m ai_module.scripts.evaluate_model

Output:
	- Console report with MAE, RMSE, R²
	- Detailed error analysis
	- Optional prediction plot
"""

import os
import sys
import argparse
import logging

import pandas as pd
import numpy as np
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


def evaluate_model(
	data_path: str = None,
	model_dir: str = None,
	sample_size: int = None,
) -> dict:
	"""
	Evaluate trained model performance.
    
	Args:
		data_path: Path to evaluation data CSV.
		model_dir: Directory containing trained model.
		sample_size: Optional number of records to evaluate.
    
	Returns:
		Dictionary with evaluation metrics.
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

	logger.info("=== Starting Model Evaluation ===")

	# Load model
	loader = ModelLoader(model_dir=model_dir)
	model = loader.load_model()

	if model is None:
		raise RuntimeError(
			"No trained model found. Please run train_model.py first."
		)

	logger.info(f"Model loaded from: {loader.load_source}")

	# Load data
	if not os.path.exists(data_path):
		raise FileNotFoundError(f"Evaluation data not found: {data_path}")

	df = pd.read_csv(data_path)

	# Sample if requested
	if sample_size and sample_size < len(df):
		df = df.sample(n=sample_size, random_state=42)
		logger.info(f"Using sample of {sample_size} records")

	logger.info(f"Evaluating on {len(df)} records")

	# Prepare features
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

	X = df[feature_columns]
	y_true = df["actual_eta_minutes"]

	# Predict
	y_pred = model.predict(X)

	# Calculate metrics
	mae = mean_absolute_error(y_true, y_pred)
	rmse = np.sqrt(mean_squared_error(y_true, y_pred))
	r2 = r2_score(y_true, y_pred)

	# Error analysis
	errors = np.abs(y_true - y_pred)
	within_1_min = np.mean(errors <= 1.0) * 100
	within_2_min = np.mean(errors <= 2.0) * 100
	within_3_min = np.mean(errors <= 3.0) * 100
	max_error = np.max(errors)

	logger.info("\n=== Evaluation Results ===")
	logger.info(f"MAE:  {mae:.3f} minutes")
	logger.info(f"RMSE: {rmse:.3f} minutes")
	logger.info(f"R²:   {r2:.3f}")

	logger.info("\n=== Accuracy Distribution ===")
	logger.info(f"Within ±1 min: {within_1_min:.1f}%")
	logger.info(f"Within ±2 min: {within_2_min:.1f}%")
	logger.info(f"Within ±3 min: {within_3_min:.1f}%")
	logger.info(f"Max error: {max_error:.2f} min")

	# Production readiness check
	threshold_mae = 3.0
	threshold_within_3 = 80.0

	is_ready = (
		mae <= threshold_mae
		and within_3_min >= threshold_within_3
	)

	if is_ready:
		logger.info("\n✅ Model is PRODUCTION READY")
	else:
		logger.warning("\n⚠️ Model needs improvement before production")

	# Compare with metadata if available
	if loader.metadata and "metrics" in loader.metadata:
		old_mae = loader.metadata["metrics"].get("mae")
		if old_mae is not None:
			diff = mae - old_mae
			if abs(diff) > 0.1:
				direction = "improved" if diff < 0 else "degraded"
				logger.info(
					f"\nModel performance {direction} by "
					f"{abs(diff):.3f} min vs metadata"
				)

	return {
		"mae": float(mae),
		"rmse": float(rmse),
		"r2_score": float(r2),
		"within_1_min_pct": float(within_1_min),
		"within_2_min_pct": float(within_2_min),
		"within_3_min_pct": float(within_3_min),
		"max_error": float(max_error),
		"is_production_ready": bool(is_ready),
		"records_evaluated": int(len(df)),
	}


def main():
	"""CLI entry point."""
	parser = argparse.ArgumentParser(
		description="Evaluate ETA prediction model"
	)
	parser.add_argument(
		"--data",
		type=str,
		default=None,
		help="Path to evaluation data CSV"
	)
	parser.add_argument(
		"--model-dir",
		type=str,
		default=None,
		help="Directory containing trained model"
	)
	parser.add_argument(
		"--sample",
		type=int,
		default=None,
		help="Evaluate on sample size (for quick testing)"
	)

	args = parser.parse_args()

	try:
		metrics = evaluate_model(
			data_path=args.data,
			model_dir=args.model_dir,
			sample_size=args.sample,
		)

		logger.info("\nEvaluation Summary:")
		logger.info(f"  MAE: {metrics['mae']:.3f} min")
		logger.info(
			f"  Within ±3 min: {metrics['within_3_min_pct']:.1f}%"
		)
		logger.info(
			f"  Production Ready: {metrics['is_production_ready']}"
		)

	except Exception as e:
		logger.error(f"❌ Evaluation failed: {str(e)}")
		sys.exit(1)


if __name__ == "__main__":
	main()
