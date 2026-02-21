"""
Runner Simulator
==================
Simulates delivery runners picking up and delivering orders.

Usage:
	python -m automation.simulation.runner_simulator
"""

import sys
import os
import time
import random
import requests

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


class RunnerSimulator:
	"""Simulates delivery runners processing deliveries."""

	def __init__(self, base_url: str = None):
		self.base_url = base_url or Config.BASE_URL
		self.tokens = {}
		self.deliveries_completed = 0
		self.running = True

	def start(
		self,
		num_runners: int = None,
		duration_seconds: int = 300,
	):
		"""
		Start runner simulation.
        
		Args:
			num_runners: Number of runners to simulate.
			duration_seconds: How long to run.
		"""
		if num_runners is None:
			num_runners = Config.TOTAL_RUNNERS

		print("=" * 50)
		print("  Runner Simulator Started")
		print("=" * 50)
		print(f"  Runners:  {num_runners}")
		print(f"  Duration: {duration_seconds} seconds")

		# Login all runners
		for i in range(1, num_runners + 1):
			runner_id = f"RUN-{i:03d}"
			token = self._login(runner_id)
			if token:
				self.tokens[runner_id] = token

		print(f"  Logged in: {len(self.tokens)} runners")

		start_time = time.time()

		while self.running:
			elapsed = time.time() - start_time
			if elapsed >= duration_seconds:
				break

			for runner_id, token in self.tokens.items():
				deliveries = self._get_deliveries(token)

				if deliveries:
					for delivery in deliveries:
						order_id = delivery.get("order_id")
						status = delivery.get("status")

						if status == "Ready":
							# Pick up
							self._update_delivery(
								order_id, "PickedUp", token
							)
							print(
								f"  📦 {runner_id}: "
								f"Picked up {order_id}"
							)

							time.sleep(random.uniform(1, 3))

							# On the way
							self._update_delivery(
								order_id, "OnTheWay", token
							)
							print(
								f"  🏃 {runner_id}: "
								f"Delivering {order_id}"
							)

							# Simulate delivery time
							delivery_time = random.uniform(
								Config.RUNNER_DELIVERY_MIN,
								Config.RUNNER_DELIVERY_MAX,
							)
							time.sleep(delivery_time)

							# Delivered
							self._update_delivery(
								order_id, "Delivered", token
							)
							self.deliveries_completed += 1
							print(
								f"  ✅ {runner_id}: "
								f"Delivered {order_id} "
								f"[Total: "
								f"{self.deliveries_completed}]"
							)

			time.sleep(2)

		print(f"\n  Runner simulation ended.")
		print(f"  Deliveries: {self.deliveries_completed}")

	def _login(self, user_id: str) -> str:
		"""Login runner."""
		try:
			response = requests.post(
				f"{self.base_url}/auth/login",
				json={
					"employee_id": user_id,
					"password": Config.DEFAULT_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code == 200:
				return response.json()["access_token"]
		except Exception:
			pass
		return None

	def _get_deliveries(self, token: str) -> list:
		"""Get assigned deliveries."""
		try:
			response = requests.get(
				f"{self.base_url}/runner/deliveries",
				headers={
					"Authorization": f"Bearer {token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code == 200:
				data = response.json()
				if isinstance(data, list):
					return data
				return data.get("deliveries", [])
		except Exception:
			pass
		return []

	def _update_delivery(
		self, order_id: str, status: str, token: str
	):
		"""Update delivery status."""
		try:
			requests.patch(
				f"{self.base_url}/runner/deliveries"
				f"/{order_id}/status",
				json={"status": status},
				headers={
					"Authorization": f"Bearer {token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
		except Exception:
			pass

	def stop(self):
		"""Stop simulator."""
		self.running = False


if __name__ == "__main__":
	sim = RunnerSimulator()
	sim.start(num_runners=5, duration_seconds=120)
