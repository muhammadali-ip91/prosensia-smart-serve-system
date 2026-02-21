"""
Kitchen Simulator
==================
Simulates kitchen staff processing orders.
Runs independently and processes orders as they arrive.

Usage:
	python -m automation.simulation.kitchen_simulator
"""

import sys
import os
import time
import random
import requests
from datetime import datetime

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


class KitchenSimulator:
	"""Simulates kitchen staff processing incoming orders."""

	def __init__(self, base_url: str = None):
		self.base_url = base_url or Config.BASE_URL
		self.token = None
		self.orders_processed = 0
		self.running = True

	def start(self, duration_seconds: int = 300):
		"""
		Start kitchen simulation.
        
		Args:
			duration_seconds: How long to run (default 5 min).
		"""
		print("=" * 50)
		print("  Kitchen Simulator Started")
		print("=" * 50)
		print(f"  Duration: {duration_seconds} seconds")
		print(f"  API URL:  {self.base_url}")

		# Login as kitchen staff
		self.token = self._login("KIT-001")
		if not self.token:
			print("❌ Kitchen login failed!")
			return

		start_time = time.time()

		while self.running:
			elapsed = time.time() - start_time
			if elapsed >= duration_seconds:
				break

			# Fetch pending orders
			orders = self._get_pending_orders()

			if orders:
				for order in orders:
					order_id = order.get("order_id")
					status = order.get("status")

					if status == "Placed" or status == "Confirmed":
						# Start preparing
						self._update_status(
							order_id, "Preparing"
						)
						print(
							f"  🍳 {order_id}: "
							f"Started preparing"
						)

						# Simulate prep time
						prep_time = random.uniform(
							Config.KITCHEN_PREP_MIN,
							Config.KITCHEN_PREP_MAX,
						)
						time.sleep(prep_time)

						# Mark ready
						self._update_status(order_id, "Ready")
						self.orders_processed += 1
						print(
							f"  ✅ {order_id}: Ready! "
							f"(prep: {prep_time:.1f}s) "
							f"[Total: {self.orders_processed}]"
						)
			else:
				# No orders, wait and check again
				time.sleep(2)

		print(f"\n  Kitchen simulation ended.")
		print(f"  Orders processed: {self.orders_processed}")

	def _login(self, user_id: str) -> str:
		"""Login and get token."""
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
		except Exception as e:
			print(f"Login error: {e}")
		return None

	def _get_pending_orders(self) -> list:
		"""Fetch orders waiting for kitchen."""
		try:
			response = requests.get(
				f"{self.base_url}/kitchen/orders",
				headers={
					"Authorization": f"Bearer {self.token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code == 200:
				data = response.json()
				if isinstance(data, list):
					return data
				return data.get("orders", [])
		except Exception:
			pass
		return []

	def _update_status(self, order_id: str, status: str):
		"""Update order status."""
		try:
			requests.patch(
				f"{self.base_url}/kitchen/orders"
				f"/{order_id}/status",
				json={"status": status},
				headers={
					"Authorization": f"Bearer {self.token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
		except Exception:
			pass

	def stop(self):
		"""Stop the simulator."""
		self.running = False


if __name__ == "__main__":
	sim = KitchenSimulator()
	sim.start(duration_seconds=120)
