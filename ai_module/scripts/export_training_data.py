"""
Export Training Data from Database Script
=========================================
Fetches real historical order delivery data from PostgreSQL
and exports it for model retraining.

Usage:
	python -m ai_module.scripts.export_training_data

Output:
	ai_module/data/training_data_from_db.csv
"""

import os
import sys
import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd
from sqlalchemy import text

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
	os.path.dirname(__file__), "..", ".."
)))

from backend.database.connection import engine

logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def export_training_data(
	days_back: int = 30,
	min_records: int = 100,
	output_path: str = None,
) -> pd.DataFrame:
	"""
	Export historical order delivery data from database.
    
	This query extracts completed orders with actual delivery times,
	then derives features needed for model training.
    
	Args:
		days_back: Number of past days to fetch data from.
		min_records: Minimum records required for retraining.
		output_path: Output CSV path.
    
	Returns:
		DataFrame with training data.
	"""
	logger.info(
		f"Exporting training data from last {days_back} days..."
	)

	# SQL query to fetch completed orders with necessary fields
	# Note: Adjust table/column names based on your actual schema
	query = text("""
		SELECT
			o.id as order_id,
			o.created_at,
			o.priority,
			o.total_items,
			o.station_id,
			s.distance_from_kitchen as station_distance,

			-- Timestamps for actual delivery time calculation
			o.created_at as order_created_at,
			o.kitchen_completed_at,
			o.delivered_at,

			-- Calculate actual ETA in minutes
			EXTRACT(EPOCH FROM (o.delivered_at - o.created_at))/60
				AS actual_eta_minutes,

			-- Queue and load context at order time (estimated)
			o.queue_position as kitchen_queue_length,
			(
				SELECT COUNT(*)
				FROM orders o2
				WHERE o2.created_at <= o.created_at
					AND o2.status IN ('pending', 'preparing', 'ready')
			) as active_orders_count,

			-- Runner availability at order time (estimated)
			(
				SELECT COUNT(*)
				FROM users u
				WHERE u.role = 'runner'
					AND u.is_available = true
			) as available_runners,

			-- Item complexity and prep time aggregation
			COALESCE(
				AVG(oi.prep_time),
				5
			) as avg_prep_time,
			COALESCE(
				AVG(oi.complexity_score),
				3
			) as item_complexity

		FROM orders o
		LEFT JOIN stations s ON o.station_id = s.id
		LEFT JOIN order_items oi ON o.id = oi.order_id

		WHERE
			o.status = 'delivered'
			AND o.delivered_at IS NOT NULL
			AND o.created_at >= NOW() - INTERVAL :days_interval
			AND o.delivered_at > o.created_at

		GROUP BY
			o.id,
			o.created_at,
			o.priority,
			o.total_items,
			o.station_id,
			s.distance_from_kitchen,
			o.kitchen_completed_at,
			o.delivered_at,
			o.queue_position

		HAVING
			EXTRACT(EPOCH FROM (o.delivered_at - o.created_at))/60
				BETWEEN 2 AND 90

		ORDER BY o.created_at DESC
	""")

	try:
		with engine.connect() as conn:
			result = conn.execute(
				query,
				{"days_interval": f"'{days_back} days'"}
			)
			rows = result.fetchall()

		if not rows:
			logger.warning("No historical delivery data found")
			return pd.DataFrame()

		# Convert to DataFrame
		df = pd.DataFrame(rows)
		logger.info(f"Fetched {len(df)} records from database")

		# Feature engineering for training
		logger.info("Processing features...")

		# Time-based features
		df['created_at'] = pd.to_datetime(df['created_at'])
		df['hour_of_day'] = df['created_at'].dt.hour
		df['day_of_week'] = df['created_at'].dt.dayofweek
		df['is_peak_hour'] = df['hour_of_day'].apply(
			lambda h: 1 if (12 <= h <= 14 or 19 <= h <= 21) else 0
		)
		df['is_weekend'] = df['day_of_week'].apply(
			lambda d: 1 if d >= 5 else 0
		)

		# Priority feature
		df['is_urgent'] = df['priority'].apply(
			lambda p: 1 if p == 'Urgent' else 0
		)

		# Rename columns to match training schema
		df = df.rename(columns={
			'total_items': 'num_items'
		})

		# Fill missing values
		df['station_distance'] = df['station_distance'].fillna(100)
		df['kitchen_queue_length'] = df['kitchen_queue_length'].fillna(0)
		df['active_orders_count'] = df['active_orders_count'].fillna(0)
		df['available_runners'] = df['available_runners'].fillna(3)
		df['avg_prep_time'] = df['avg_prep_time'].fillna(5)
		df['item_complexity'] = df['item_complexity'].fillna(3)

		# Select final training columns
		training_columns = [
			'hour_of_day',
			'day_of_week',
			'is_peak_hour',
			'is_weekend',
			'num_items',
			'item_complexity',
			'avg_prep_time',
			'station_distance',
			'active_orders_count',
			'kitchen_queue_length',
			'available_runners',
			'is_urgent',
			'actual_eta_minutes',
		]

		training_df = df[training_columns].copy()

		# Remove outliers (optional but recommended)
		q1 = training_df['actual_eta_minutes'].quantile(0.01)
		q99 = training_df['actual_eta_minutes'].quantile(0.99)
		training_df = training_df[
			(training_df['actual_eta_minutes'] >= q1)
			& (training_df['actual_eta_minutes'] <= q99)
		]

		logger.info(
			f"After outlier removal: {len(training_df)} records"
		)

		# Check minimum records requirement
		if len(training_df) < min_records:
			logger.warning(
				f"Insufficient records for retraining: "
				f"{len(training_df)} < {min_records}"
			)

		# Save to CSV
		if output_path is None:
			output_path = os.path.join(
				os.path.dirname(os.path.dirname(__file__)),
				"data",
				"training_data_from_db.csv"
			)

		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		training_df.to_csv(output_path, index=False)

		logger.info(f"Training data exported to: {output_path}")

		# Print summary
		logger.info("\n=== Export Summary ===")
		logger.info(f"Records exported: {len(training_df)}")
		logger.info(
			f"Average ETA: {training_df['actual_eta_minutes'].mean():.2f} min"
		)
		logger.info(
			f"ETA range: "
			f"{training_df['actual_eta_minutes'].min():.2f} - "
			f"{training_df['actual_eta_minutes'].max():.2f} min"
		)

		return training_df

	except Exception as e:
		logger.error(f"Failed to export training data: {str(e)}")
		raise


def main():
	"""CLI entry point."""
	parser = argparse.ArgumentParser(
		description="Export training data from database"
	)
	parser.add_argument(
		"--days",
		type=int,
		default=30,
		help="Days of historical data to fetch (default: 30)"
	)
	parser.add_argument(
		"--min-records",
		type=int,
		default=100,
		help="Minimum records required (default: 100)"
	)
	parser.add_argument(
		"--output",
		type=str,
		default=None,
		help="Output CSV path"
	)

	args = parser.parse_args()

	try:
		df = export_training_data(
			days_back=args.days,
			min_records=args.min_records,
			output_path=args.output,
		)

		if len(df) > 0:
			logger.info("✅ Export completed successfully!")
		else:
			logger.warning("⚠️ No data exported")

	except Exception as e:
		logger.error(f"❌ Export failed: {str(e)}")
		sys.exit(1)


if __name__ == "__main__":
	main()
