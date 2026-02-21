"""
Model Retraining Script
=======================
Retrains ETA model with latest data and validates performance.

This script:
1. Loads latest training data
2. Trains new model
3. Evaluates new model
4. Compares with current model
5. Replaces current model ONLY if new model is better

Usage:
	python -m ai_module.scripts.retrain
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
	os.path.dirname(__file__), "..", ".."
)))

from ai_module.scripts.train_model import train_model
from ai_module.scripts.evaluate_model import evaluate_model
from ai_module.core.model_loader import ModelLoader

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def retrain_model(
	data_path: str = None,
	model_dir: str = None,
	improvement_threshold: float = 0.1,
) -> dict:
	"""
	Retrain model and replace current if improved.
    
	Args:
		data_path: Path to training data.
		model_dir: Model directory.
		improvement_threshold: Minimum MAE improvement required.
    
	Returns:
		Dictionary with retraining results.
	"""
	if model_dir is None:
		model_dir = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"models"
		)

	logger.info("=" * 60)
	logger.info("STARTING MODEL RETRAINING")
	logger.info("=" * 60)

	# Step 1: Get current model metrics
	logger.info("\n[Step 1/4] Loading current model metrics...")
	loader = ModelLoader(model_dir=model_dir)
	current_model = loader.load_model()

	current_mae = None
	if loader.metadata and "metrics" in loader.metadata:
		current_mae = loader.metadata["metrics"].get("mae")
		logger.info(f"Current model MAE: {current_mae:.3f} min")
	else:
		logger.info("No current model metadata found")

	# Step 2: Train new model (this automatically backs up old model)
	logger.info("\n[Step 2/4] Training new model...")
	train_metrics = train_model(
		data_path=data_path,
		model_dir=model_dir,
	)
	new_mae = train_metrics["mae"]
	logger.info(f"New model MAE: {new_mae:.3f} min")

	# Step 3: Evaluate new model
	logger.info("\n[Step 3/4] Evaluating new model...")
	eval_metrics = evaluate_model(
		data_path=data_path,
		model_dir=model_dir,
		sample_size=2000,  # Quick evaluation
	)

	# Step 4: Compare and decide
	logger.info("\n[Step 4/4] Comparing models...")

	should_deploy = False
	reason = ""

	if current_mae is None:
		# No previous model, deploy new one
		should_deploy = True
		reason = "No previous model exists"
	else:
		improvement = current_mae - new_mae

		if improvement >= improvement_threshold:
			should_deploy = True
			reason = (
				f"Model improved by {improvement:.3f} min "
				f"(threshold: {improvement_threshold:.3f})"
			)
		elif new_mae <= 3.0 and current_mae > 3.0:
			# New model meets threshold while old didn't
			should_deploy = True
			reason = (
				"New model meets production threshold, "
				"old model did not"
			)
		else:
			should_deploy = False
			reason = (
				f"Improvement ({improvement:.3f}) below threshold "
				f"({improvement_threshold:.3f})"
			)

	# If not deploying, restore backup
	if not should_deploy:
		logger.warning("\nNew model not better enough. Restoring old model...")

		# Restore backup model
		backup_path = os.path.join(model_dir, "eta_model_backup.pkl")
		model_path = os.path.join(model_dir, "eta_model.pkl")

		if os.path.exists(backup_path):
			import shutil
			shutil.copy2(backup_path, model_path)
			logger.info("Old model restored from backup")
		else:
			logger.error("Backup model not found! Keeping new model.")
			should_deploy = True
			reason = "Backup not found, kept new model"

	# Final summary
	logger.info("\n" + "=" * 60)
	logger.info("RETRAINING SUMMARY")
	logger.info("=" * 60)
	logger.info(f"Current MAE: {current_mae if current_mae else 'N/A'}")
	logger.info(f"New MAE: {new_mae:.3f}")
	logger.info(
		f"Decision: {'✅ DEPLOYED' if should_deploy else '❌ REJECTED'}"
	)
	logger.info(f"Reason: {reason}")

	result = {
		"timestamp": datetime.now().isoformat(),
		"current_mae": float(current_mae) if current_mae else None,
		"new_mae": float(new_mae),
		"improvement": (
			float(current_mae - new_mae)
			if current_mae else None
		),
		"deployed": bool(should_deploy),
		"reason": reason,
		"eval_metrics": eval_metrics,
	}

	return result


def main():
	"""CLI entry point."""
	try:
		result = retrain_model()

		if result["deployed"]:
			logger.info("\n✅ Retraining successful - new model deployed")
			sys.exit(0)
		else:
			logger.info("\n⚠️ Retraining completed - old model retained")
			sys.exit(0)

	except Exception as e:
		logger.error(f"\n❌ Retraining failed: {str(e)}")
		sys.exit(1)


if __name__ == "__main__":
	main()
