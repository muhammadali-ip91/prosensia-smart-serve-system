"""Runner Assignment Algorithm - Smart Runner Selection"""

from sqlalchemy.orm import Session
from typing import Optional
from loguru import logger

from models.runner_model import Runner
from models.station_model import Station
from models.order_model import Order
from utils.constants import RunnerStatus, OrderStatus


def _reconcile_runner_workloads(db: Session):
	"""Recalculate runner active load from active orders to avoid stale counters."""

	runners = db.query(Runner).all()
	for runner in runners:
		active_count = db.query(Order).filter(
			Order.runner_id == runner.runner_id,
			Order.status.in_(OrderStatus.ACTIVE)
		).count()

		runner.active_order_count = active_count

		if runner.current_status != RunnerStatus.OFFLINE:
			if active_count >= runner.max_capacity * 0.8:
				runner.current_status = RunnerStatus.BUSY
			elif runner.current_status == RunnerStatus.BUSY and active_count == 0:
				runner.current_status = RunnerStatus.AVAILABLE

	db.flush()


def assign_optimal_runner(db: Session, priority: str, station_id: str) -> Optional[Runner]:
	"""
	Assigns the best available runner based on weighted factors:
	1. Current Load (40%)
	2. Distance to Station (30%)
	3. Performance / Avg Delivery Time (20%)
	4. Total Capacity Remaining (10%)
	"""

	_reconcile_runner_workloads(db)

	# Get all available runners
	available_runners = db.query(Runner).filter(
		Runner.current_status.in_([RunnerStatus.AVAILABLE, RunnerStatus.BUSY]),
		Runner.active_order_count < Runner.max_capacity
	).all()

	if not available_runners:
		logger.warning(f"No runners available for order at {station_id}")
		return None

	# Get station distance
	station = db.query(Station).filter(Station.station_id == station_id).first()
	station_distance = station.distance_from_kitchen if station else 200

	# Max values for normalization
	max_capacity = max(r.max_capacity for r in available_runners)
	max_distance = 500  # Maximum possible distance
	max_avg_time = 30   # Maximum average delivery time

	# URGENT ORDER: Get least loaded runner directly
	if priority == "Urgent":
		least_loaded = min(available_runners, key=lambda r: r.active_order_count)

		# Try to find a runner with very few orders
		if least_loaded.active_order_count >= 3:
			lightly_loaded = [r for r in available_runners if r.active_order_count <= 1]
			if lightly_loaded:
				least_loaded = lightly_loaded[0]

		# Update runner
		least_loaded.active_order_count += 1
		if least_loaded.active_order_count >= least_loaded.max_capacity * 0.8:
			least_loaded.current_status = RunnerStatus.BUSY

		db.flush()
		logger.info(f"Urgent order: Assigned Runner {least_loaded.runner_id}")
		return least_loaded

	# REGULAR ORDER: Multi-factor scoring
	scored_runners = []

	for runner in available_runners:

		# Factor 1: Load Score (lower = better) - Weight: 40%
		load_score = runner.active_order_count / max(runner.max_capacity, 1)

		# Factor 2: Capacity Remaining (higher remaining = better) - Weight: 10%
		capacity_score = 1 - ((runner.max_capacity - runner.active_order_count) / max(max_capacity, 1))

		# Factor 3: Performance Score (lower avg time = better) - Weight: 20%
		if runner.average_delivery_time > 0:
			performance_score = runner.average_delivery_time / max_avg_time
		else:
			performance_score = 0.5  # Default for new runners

		# Factor 4: Distance approximation (lower = better) - Weight: 30%
		# Simple: Runners with fewer orders likely closer to kitchen
		distance_score = runner.active_order_count * 0.2

		# Weighted Total (lower = better candidate)
		total_score = (
			load_score * 0.40 +
			distance_score * 0.30 +
			performance_score * 0.20 +
			capacity_score * 0.10
		)

		scored_runners.append((runner, total_score))

	# Sort by score (lowest first = best)
	scored_runners.sort(key=lambda x: x[1])

	# Select best runner
	best_runner = scored_runners[0][0]

	# Update runner
	best_runner.active_order_count += 1
	if best_runner.active_order_count >= best_runner.max_capacity * 0.8:
		best_runner.current_status = RunnerStatus.BUSY

	db.flush()

	logger.info(
		f"Runner Assignment: {best_runner.runner_id} "
		f"(Score: {scored_runners[0][1]:.3f}, "
		f"Load: {best_runner.active_order_count}/{best_runner.max_capacity})"
	)

	return best_runner

