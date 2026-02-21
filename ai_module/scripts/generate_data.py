"""
Generate Synthetic Training Data Script
=======================================
Creates realistic training data for ETA prediction model.

Usage:
	python -m ai_module.scripts.generate_data --records 5000

Output:
	ai_module/data/training_data.csv
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
	os.path.dirname(__file__), "..", ".."
)))

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_data(
	num_records: int = 5000,
	output_path: str = None,
	random_seed: int = 42,
) -> pd.DataFrame:
	"""
	Generate synthetic training data for ETA model.
    
	Creates realistic order scenarios with features and target ETA.
	The target ETA includes realistic noise to simulate real-world
	delivery variations.
    
	Args:
		num_records: Number of synthetic records to generate.
		output_path: Where to save CSV file. If None, uses default path.
		random_seed: Random seed for reproducibility.
    
	Returns:
		pandas DataFrame with synthetic training data.
	"""
	logger.info(
		f"Generating {num_records} synthetic training records..."
	)

	# Set random seed for reproducibility
	np.random.seed(random_seed)
	random.seed(random_seed)

	records = []

	for i in range(num_records):
		# Generate time context
		hour = np.random.randint(8, 23)  # Operating hours: 8 AM - 10 PM
		day_of_week = np.random.randint(0, 7)  # 0=Monday, 6=Sunday

		# Peak hours: lunch (12-14) and dinner (19-21)
		is_peak_hour = (
			1 if (12 <= hour <= 14 or 19 <= hour <= 21) else 0
		)

		# Weekend flag
		is_weekend = 1 if day_of_week >= 5 else 0

		# Order characteristics
		num_items = np.random.randint(1, 8)

		# More complex items are slightly less frequent
		item_complexity = np.random.choice(
			[1, 2, 3, 4, 5, 6, 7],
			p=[0.15, 0.20, 0.20, 0.18, 0.12, 0.10, 0.05]
		)

		# Base prep time depends on complexity and quantity
		avg_prep_time = (
			3 + item_complexity * 1.8 + num_items * 0.8
		)
		avg_prep_time += np.random.normal(0, 1.5)  # natural variation
		avg_prep_time = max(2, avg_prep_time)

		# Distance to station (meters)
		station_distance = np.random.randint(30, 350)

		# System state
		active_orders_count = np.random.randint(0, 35)
		kitchen_queue_length = np.random.randint(0, 20)
		available_runners = np.random.randint(1, 8)

		# Priority distribution (most are regular)
		priority = np.random.choice(
			["Regular", "Urgent"],
			p=[0.88, 0.12]
		)
		is_urgent = 1 if priority == "Urgent" else 0

		# ========================================
		# Simulate realistic ETA (TARGET VARIABLE)
		# ========================================
		# Base formula (similar to fallback logic but with richer factors)
		eta = (
			avg_prep_time * 0.9
			+ kitchen_queue_length * 1.4
			+ station_distance * 0.018
			+ num_items * 0.7
		)

		# Peak hour effect
		if is_peak_hour:
			eta *= 1.25

		# Weekend effect (slightly slower due to higher traffic)
		if is_weekend:
			eta *= 1.08

		# Runner availability effect
		if available_runners <= 2:
			eta += 5.5
		elif available_runners <= 4:
			eta += 2.0
		else:
			eta -= 1.0

		# Urgent orders get prioritized
		if is_urgent:
			eta *= 0.82

		# Add random noise to simulate real-world unpredictability
		noise = np.random.normal(0, 2.2)
		eta += noise

		# Clamp to realistic range
		eta = max(3, min(60, eta))

		record = {
			"hour_of_day": hour,
			"day_of_week": day_of_week,
			"is_peak_hour": is_peak_hour,
			"is_weekend": is_weekend,
			"num_items": num_items,
			"item_complexity": item_complexity,
			"avg_prep_time": round(avg_prep_time, 2),
			"station_distance": station_distance,
			"active_orders_count": active_orders_count,
			"kitchen_queue_length": kitchen_queue_length,
			"available_runners": available_runners,
			"is_urgent": is_urgent,
			"actual_eta_minutes": round(eta, 2),
		}
		records.append(record)

		if (i + 1) % 1000 == 0:
			logger.info(f"Generated {i + 1}/{num_records} records...")

	# Create DataFrame
	df = pd.DataFrame(records)

	# Save if output path provided
	if output_path is None:
		output_path = os.path.join(
			os.path.dirname(os.path.dirname(__file__)),
			"data",
			"training_data.csv"
		)

	# Ensure directory exists
	os.makedirs(os.path.dirname(output_path), exist_ok=True)

	# Save to CSV
	df.to_csv(output_path, index=False)
	logger.info(f"Training data saved to: {output_path}")

	# Print summary statistics
	logger.info("\n=== Data Generation Summary ===")
	logger.info(f"Total records: {len(df)}")
	logger.info(
		f"Average ETA: {df['actual_eta_minutes'].mean():.2f} min"
	)
	logger.info(
		f"ETA range: {df['actual_eta_minutes'].min():.2f} - "
		f"{df['actual_eta_minutes'].max():.2f} min"
	)
	logger.info(
		f"Urgent orders: {df['is_urgent'].sum()} "
		f"({df['is_urgent'].mean() * 100:.1f}%)"
	)
	logger.info(
		f"Peak hour orders: {df['is_peak_hour'].sum()} "
		f"({df['is_peak_hour'].mean() * 100:.1f}%)"
	)

	return df


def main():
	"""CLI entry point."""
	parser = argparse.ArgumentParser(
		description="Generate synthetic training data for ETA model"
	)
	parser.add_argument(
		"--records",
		type=int,
		default=5000,
		help="Number of records to generate (default: 5000)"
	)
	parser.add_argument(
		"--output",
		type=str,
		default=None,
		help="Output CSV path (default: ai_module/data/training_data.csv)"
	)
	parser.add_argument(
		"--seed",
		type=int,
		default=42,
		help="Random seed for reproducibility (default: 42)"
	)

	args = parser.parse_args()

	generate_synthetic_data(
		num_records=args.records,
		output_path=args.output,
		random_seed=args.seed,
	)

	logger.info("✅ Data generation completed successfully!")


if __name__ == "__main__":
	main()
