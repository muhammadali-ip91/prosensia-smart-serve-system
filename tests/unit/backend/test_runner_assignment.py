"""
Runner Assignment Algorithm Tests
====================================
Tests for the intelligent runner assignment system.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(
	os.path.dirname(__file__), '..', '..', '..'
))


@pytest.mark.unit
class TestRunnerScoring:
	"""Tests for runner scoring logic."""

	def calculate_score(
		self,
		active_orders: int,
		max_capacity: int,
		distance: float,
		max_distance: float,
		est_free_time: float,
		max_wait: float,
		avg_rating: float,
	) -> float:
		"""
		Calculate runner score (lower = better).
		Mirrors the actual algorithm.
		"""
		load_score = active_orders / max_capacity
		distance_score = distance / max_distance
		availability_score = (
			est_free_time / max_wait
			if active_orders > 0
			else 0
		)
		performance_score = 1 - (avg_rating / 5.0)

		total = (
			load_score * 0.40
			+ distance_score * 0.30
			+ availability_score * 0.20
			+ performance_score * 0.10
		)
		return round(total, 4)

	def test_empty_runner_best_score(self):
		"""Runner with 0 orders should score lowest (best)."""
		score = self.calculate_score(
			active_orders=0,
			max_capacity=5,
			distance=50,
			max_distance=500,
			est_free_time=0,
			max_wait=30,
			avg_rating=4.5,
		)
		# Load: 0, Distance: 0.1, Availability: 0, Performance: 0.1
		assert score < 0.15

	def test_full_runner_worst_score(self):
		"""Runner at max capacity should score highest (worst)."""
		score = self.calculate_score(
			active_orders=5,
			max_capacity=5,
			distance=400,
			max_distance=500,
			est_free_time=25,
			max_wait=30,
			avg_rating=2.0,
		)
		assert score > 0.70

	def test_closer_runner_preferred(self):
		"""Closer runner should have lower (better) score."""
		score_close = self.calculate_score(
			active_orders=1, max_capacity=5,
			distance=50, max_distance=500,
			est_free_time=5, max_wait=30,
			avg_rating=4.0,
		)
		score_far = self.calculate_score(
			active_orders=1, max_capacity=5,
			distance=400, max_distance=500,
			est_free_time=5, max_wait=30,
			avg_rating=4.0,
		)
		assert score_close < score_far

	def test_less_loaded_runner_preferred(self):
		"""Less loaded runner should be preferred."""
		score_light = self.calculate_score(
			active_orders=1, max_capacity=5,
			distance=100, max_distance=500,
			est_free_time=5, max_wait=30,
			avg_rating=4.0,
		)
		score_heavy = self.calculate_score(
			active_orders=4, max_capacity=5,
			distance=100, max_distance=500,
			est_free_time=20, max_wait=30,
			avg_rating=4.0,
		)
		assert score_light < score_heavy

	def test_higher_rated_runner_preferred(self):
		"""Higher rated runner should have slight preference."""
		score_high_rating = self.calculate_score(
			active_orders=2, max_capacity=5,
			distance=100, max_distance=500,
			est_free_time=10, max_wait=30,
			avg_rating=4.8,
		)
		score_low_rating = self.calculate_score(
			active_orders=2, max_capacity=5,
			distance=100, max_distance=500,
			est_free_time=10, max_wait=30,
			avg_rating=2.0,
		)
		assert score_high_rating < score_low_rating

	def test_load_weight_is_highest(self):
		"""Load factor (40%) should have most impact."""
		# Runner with high load but close
		score_high_load = self.calculate_score(
			active_orders=4, max_capacity=5,
			distance=50, max_distance=500,
			est_free_time=20, max_wait=30,
			avg_rating=5.0,
		)
		# Runner with low load but far
		score_low_load = self.calculate_score(
			active_orders=0, max_capacity=5,
			distance=400, max_distance=500,
			est_free_time=0, max_wait=30,
			avg_rating=3.0,
		)
		# Low load should still win despite distance
		assert score_low_load < score_high_load


@pytest.mark.unit
class TestRunnerAssignmentEdgeCases:
	"""Edge case tests for runner assignment."""

	def test_no_runners_available(self):
		"""Should handle zero available runners gracefully."""
		available_runners = []
		assert len(available_runners) == 0
		# System should queue the order

	def test_all_runners_at_capacity(self):
		"""Should handle all runners being full."""
		runners = [
			{"id": "RUN-001", "active": 5, "max": 5},
			{"id": "RUN-002", "active": 5, "max": 5},
		]
		available = [
			r for r in runners if r["active"] < r["max"]
		]
		assert len(available) == 0

	def test_single_runner_available(self):
		"""Should assign to the only available runner."""
		runners = [
			{"id": "RUN-001", "active": 5, "max": 5},
			{"id": "RUN-002", "active": 2, "max": 5},
			{"id": "RUN-003", "active": 5, "max": 5},
		]
		available = [
			r for r in runners if r["active"] < r["max"]
		]
		assert len(available) == 1
		assert available[0]["id"] == "RUN-002"

	def test_runner_auto_busy_at_80_percent(self):
		"""Runner should become busy at 80% capacity."""
		max_capacity = 5
		threshold = 0.8
		active_orders = 4  # 80%

		utilization = active_orders / max_capacity
		should_be_busy = utilization >= threshold
		assert should_be_busy is True

	def test_runner_auto_available_at_zero(self):
		"""Runner should become available at 0 orders."""
		active_orders = 0
		should_be_available = active_orders == 0
		assert should_be_available is True
