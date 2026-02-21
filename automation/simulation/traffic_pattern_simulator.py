"""
Traffic Pattern Simulator
===========================
Simulates realistic traffic patterns throughout the day:
- Low traffic during off-peak hours
- High traffic during lunch and dinner rush
- Variable patterns based on day of week

Usage:
	python -m automation.simulation.traffic_pattern_simulator
"""

import sys
import os
import time
import random
import requests
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


class TrafficPatternSimulator:
	"""Simulates varying traffic patterns."""

	# Orders per minute for each time period
	TRAFFIC_PATTERNS = {
		"off_peak": {"orders_per_minute": 2, "urgent_pct": 10},
		"normal": {"orders_per_minute": 5, "urgent_pct": 15},
		"peak": {"orders_per_minute": 12, "urgent_pct": 25},
		"super_peak": {"orders_per_minute": 20, "urgent_pct": 30},
	}

	def __init__(self, base_url: str = None):
		self.base_url = base_url or Config.BASE_URL
		self.total_orders = 0
		self.successful = 0
		self.failed = 0
		self.lock = threading.Lock()

	def simulate_hour(
		self,
		hour: int,
		duration_seconds: int = 60,
	) -> dict:
		"""
		Simulate traffic for a specific hour.
        
		Args:
			hour: Hour of day (0-23).
			duration_seconds: How long to simulate this hour.
        
		Returns:
			Results for this hour.
		"""
		pattern = self._get_pattern_for_hour(hour)
		orders_per_min = pattern["orders_per_minute"]
		urgent_pct = pattern["urgent_pct"]

		total_orders = int(
			orders_per_min * (duration_seconds / 60)
		)
		interval = duration_seconds / max(total_orders, 1)

		print(
			f"\n  Hour {hour:02d}:00 | "
			f"Pattern: {self._get_pattern_name(hour):10s} | "
			f"Orders: {total_orders:>3d} | "
			f"Urgent: {urgent_pct}%"
		)

		for i in range(total_orders):
			threading.Thread(
				target=self._place_random_order,
				args=(urgent_pct,),
				daemon=True,
			).start()

			time.sleep(interval)

		return {
			"hour": hour,
			"pattern": self._get_pattern_name(hour),
			"orders_submitted": total_orders,
			"urgent_percentage": urgent_pct,
		}

	def simulate_full_day(
		self,
		seconds_per_hour: int = 30,
	) -> dict:
		"""
		Simulate a full working day (9 AM to 8 PM).
        
		Args:
			seconds_per_hour: Real seconds to simulate each hour.
		"""
		print("=" * 60)
		print("  Traffic Pattern Simulator - Full Day")
		print("=" * 60)
		print(f"  Seconds per hour: {seconds_per_hour}")

		results = []
		start_time = time.time()

		for hour in range(9, 21):  # 9 AM to 8 PM
			result = self.simulate_hour(
				hour, seconds_per_hour
			)
			results.append(result)

		elapsed = time.time() - start_time

		print(f"\n{'='*60}")
		print(f"  DAY SIMULATION COMPLETE")
		print(f"{'='*60}")
		print(f"  Total Orders: {self.total_orders}")
		print(f"  Successful:   {self.successful}")
		print(f"  Failed:       {self.failed}")
		print(f"  Time:         {elapsed:.1f}s")
		print(f"{'='*60}")

		return {
			"hours": results,
			"total_orders": self.total_orders,
			"successful": self.successful,
			"failed": self.failed,
		}

	def _get_pattern_for_hour(self, hour: int) -> dict:
		"""Get traffic pattern for a given hour."""
		if hour in (13,):  # Peak lunch
			return self.TRAFFIC_PATTERNS["super_peak"]
		elif 12 <= hour <= 14:  # Lunch hours
			return self.TRAFFIC_PATTERNS["peak"]
		elif 18 <= hour <= 20:  # Dinner hours
			return self.TRAFFIC_PATTERNS["peak"]
		elif 9 <= hour <= 11 or 15 <= hour <= 17:
			return self.TRAFFIC_PATTERNS["normal"]
		else:
			return self.TRAFFIC_PATTERNS["off_peak"]

	def _get_pattern_name(self, hour: int) -> str:
		"""Get human-readable pattern name."""
		if hour == 13:
			return "SUPER PEAK"
		elif 12 <= hour <= 14 or 18 <= hour <= 20:
			return "PEAK"
		elif 9 <= hour <= 11 or 15 <= hour <= 17:
			return "NORMAL"
		else:
			return "OFF-PEAK"

	def _place_random_order(self, urgent_pct: int):
		"""Place a random order."""
		eng_id = f"ENG-{random.randint(1, Config.TOTAL_ENGINEERS):03d}"

		try:
			# Login
			response = requests.post(
				f"{self.base_url}/auth/login",
				json={
					"employee_id": eng_id,
					"password": Config.DEFAULT_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code != 200:
				with self.lock:
					self.failed += 1
					self.total_orders += 1
				return

			token = response.json()["access_token"]

			# Place order
			items = random.sample(
				Config.MENU_ITEMS,
				random.randint(1, 3)
			)
			order_data = {
				"station_id": random.choice(Config.get_stations()),
				"items": [
					{
						"item_id": item["id"],
						"quantity": random.randint(1, 2),
					}
					for item in items
				],
				"priority": (
					"Urgent"
					if random.randint(1, 100) <= urgent_pct
					else "Regular"
				),
			}

			response = requests.post(
				f"{self.base_url}/orders",
				json=order_data,
				headers={
					"Authorization": f"Bearer {token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)

			with self.lock:
				self.total_orders += 1
				if response.status_code in (200, 201):
					self.successful += 1
				else:
					self.failed += 1

		except Exception:
			with self.lock:
				self.total_orders += 1
				self.failed += 1


if __name__ == "__main__":
	sim = TrafficPatternSimulator()
	sim.simulate_full_day(seconds_per_hour=15)
