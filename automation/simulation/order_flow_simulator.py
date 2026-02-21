"""
Order Flow Simulator
======================
Simulates the complete order lifecycle:
  Place → Confirm → Prepare → Ready → Pickup → Deliver

This script creates realistic order flows by:
1. Engineer places order
2. Wait for kitchen to start preparing
3. Kitchen marks as preparing, then ready
4. Runner picks up and delivers
5. Logs actual delivery time for AI training

Usage:
	python -m automation.simulation.order_flow_simulator
"""

import sys
import os
import time
import random
import requests
import threading
from datetime import datetime
from typing import Dict, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


class OrderFlowSimulator:
	"""
	Simulates complete order lifecycle flows.
	"""

	def __init__(self, base_url: str = None):
		"""Initialize simulator."""
		self.base_url = base_url or Config.BASE_URL
		self.results = {
			"total_orders": 0,
			"successful": 0,
			"failed": 0,
			"cancelled": 0,
			"total_delivery_time": 0,
			"api_response_times": [],
			"errors": [],
			"order_details": [],
		}
		self.lock = threading.Lock()
		self._tokens = {}  # Cache tokens

	def run(
		self,
		num_engineers: int = None,
		orders_per_engineer: int = None,
		max_workers: int = None,
	) -> Dict:
		"""
		Run the simulation.
        
		Args:
			num_engineers: Number of virtual engineers.
			orders_per_engineer: Orders each engineer places.
			max_workers: Maximum concurrent threads.
        
		Returns:
			Results dictionary.
		"""
		if num_engineers is None:
			num_engineers = Config.TOTAL_ENGINEERS
		if orders_per_engineer is None:
			orders_per_engineer = Config.ORDERS_PER_ENGINEER
		if max_workers is None:
			max_workers = Config.THREAD_POOL_SIZE

		total_orders = num_engineers * orders_per_engineer

		print("=" * 60)
		print("  ProSensia Smart-Serve")
		print("  Order Flow Simulator")
		print("=" * 60)
		print(f"\n  Engineers:       {num_engineers}")
		print(f"  Orders/Engineer: {orders_per_engineer}")
		print(f"  Total Orders:    {total_orders}")
		print(f"  Max Workers:     {max_workers}")
		print(f"  API URL:         {self.base_url}")
		print(f"  Started at:      {datetime.now().isoformat()}")
		print()

		start_time = time.time()

		# Create thread pool and submit tasks
		with ThreadPoolExecutor(max_workers=max_workers) as executor:
			futures = []

			for eng_idx in range(1, num_engineers + 1):
				engineer_id = f"ENG-{eng_idx:03d}"

				for order_num in range(1, orders_per_engineer + 1):
					future = executor.submit(
						self._simulate_single_order,
						engineer_id,
						order_num,
					)
					futures.append(future)

					# Stagger order submissions
					delay = random.uniform(
						Config.ORDER_INTERVAL_MIN,
						Config.ORDER_INTERVAL_MAX,
					)
					time.sleep(delay / max_workers)

			# Wait for all orders to complete
			completed = 0
			for future in as_completed(futures):
				completed += 1
				if completed % 50 == 0:
					print(
						f"  Progress: {completed}/{total_orders} "
						f"orders completed..."
					)
				try:
					future.result()
				except Exception as e:
					with self.lock:
						self.results["errors"].append(str(e))

		elapsed = time.time() - start_time
		self.results["total_time_seconds"] = round(elapsed, 2)

		# Calculate averages
		if self.results["api_response_times"]:
			times = self.results["api_response_times"]
			self.results["avg_response_time_ms"] = round(
				sum(times) / len(times), 2
			)
			self.results["max_response_time_ms"] = round(
				max(times), 2
			)
			self.results["min_response_time_ms"] = round(
				min(times), 2
			)
			# Percentiles
			sorted_times = sorted(times)
			p50 = sorted_times[len(sorted_times) // 2]
			p95 = sorted_times[int(len(sorted_times) * 0.95)]
			p99 = sorted_times[int(len(sorted_times) * 0.99)]
			self.results["p50_response_ms"] = round(p50, 2)
			self.results["p95_response_ms"] = round(p95, 2)
			self.results["p99_response_ms"] = round(p99, 2)

		if self.results["successful"] > 0:
			self.results["avg_delivery_time_min"] = round(
				self.results["total_delivery_time"]
				/ self.results["successful"],
				2
			)

		self._print_results()
		return self.results

	def _simulate_single_order(
		self,
		engineer_id: str,
		order_num: int,
	) -> None:
		"""
		Simulate a single complete order flow.
        
		Steps:
		1. Login as engineer
		2. Place order
		3. Simulate kitchen preparation
		4. Simulate runner delivery
		5. Log results
		"""
		order_start = time.time()

		try:
			# Step 1: Login
			token = self._get_token(engineer_id)
			if not token:
				with self.lock:
					self.results["failed"] += 1
					self.results["total_orders"] += 1
					self.results["errors"].append(
						f"{engineer_id}: Login failed"
					)
				return

			# Step 2: Place Order
			order = self._place_order(engineer_id, token)
			if not order:
				with self.lock:
					self.results["failed"] += 1
					self.results["total_orders"] += 1
				return

			order_id = order.get("order_id")

			# Random cancellation (5% chance)
			if random.random() < Config.CANCELLATION_RATE:
				self._cancel_order(order_id, token)
				with self.lock:
					self.results["cancelled"] += 1
					self.results["total_orders"] += 1
				return

			# Step 3: Simulate Kitchen
			kitchen_token = self._get_token("KIT-001")
			if kitchen_token:
				self._simulate_kitchen(order_id, kitchen_token)

			# Step 4: Simulate Runner Delivery
			runner_id = order.get("assigned_runner")
			if runner_id:
				runner_token = self._get_token(runner_id)
				if runner_token:
					self._simulate_delivery(
						order_id, runner_token
					)

			# Calculate delivery time
			delivery_time = time.time() - order_start

			with self.lock:
				self.results["successful"] += 1
				self.results["total_orders"] += 1
				self.results["total_delivery_time"] += delivery_time
				self.results["order_details"].append({
					"order_id": order_id,
					"engineer_id": engineer_id,
					"delivery_time_seconds": round(delivery_time, 2),
					"predicted_eta": order.get(
						"estimated_wait_time"
					),
				})

		except Exception as e:
			with self.lock:
				self.results["failed"] += 1
				self.results["total_orders"] += 1
				self.results["errors"].append(
					f"{engineer_id} order #{order_num}: {str(e)}"
				)

	def _get_token(self, user_id: str) -> Optional[str]:
		"""Get or cache JWT token for a user."""
		if user_id in self._tokens:
			return self._tokens[user_id]

		try:
			start = time.time()
			response = requests.post(
				f"{self.base_url}/auth/login",
				json={
					"employee_id": user_id,
					"password": Config.DEFAULT_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			elapsed_ms = (time.time() - start) * 1000

			with self.lock:
				self.results["api_response_times"].append(elapsed_ms)

			if response.status_code == 200:
				token = response.json().get("access_token")
				self._tokens[user_id] = token
				return token
			return None

		except Exception:
			return None

	def _place_order(
		self, engineer_id: str, token: str
	) -> Optional[Dict]:
		"""Place a new order."""
		# Select random items
		num_items = random.randint(1, Config.MAX_ITEMS_PER_ORDER)
		items = random.sample(
			Config.MENU_ITEMS,
			min(num_items, len(Config.MENU_ITEMS))
		)

		order_items = [
			{
				"item_id": item["id"],
				"quantity": random.randint(1, 3),
			}
			for item in items
		]

		# Select random station
		station = random.choice(Config.get_stations())

		# Determine priority
		priority = (
			"Urgent"
			if random.randint(1, 100) <= Config.URGENT_ORDER_PERCENTAGE
			else "Regular"
		)

		# Special instructions (30% chance)
		instructions = None
		if random.random() < 0.30:
			instructions = random.choice([
				"Less spicy please",
				"Extra sauce",
				"No onions",
				"Pack separately",
				"Make it hot",
				"No salt in raita",
			])

		order_data = {
			"station_id": station,
			"items": order_items,
			"priority": priority,
			"special_instructions": instructions,
		}

		try:
			start = time.time()
			response = requests.post(
				f"{self.base_url}/orders",
				json=order_data,
				headers={
					"Authorization": f"Bearer {token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			elapsed_ms = (time.time() - start) * 1000

			with self.lock:
				self.results["api_response_times"].append(elapsed_ms)

			if response.status_code in (200, 201):
				return response.json()
			else:
				with self.lock:
					self.results["errors"].append(
						f"Order failed: {response.status_code} "
						f"- {response.text[:100]}"
					)
				return None

		except Exception as e:
			with self.lock:
				self.results["errors"].append(
					f"Order request failed: {str(e)}"
				)
			return None

	def _cancel_order(self, order_id: str, token: str) -> None:
		"""Cancel an order."""
		try:
			requests.delete(
				f"{self.base_url}/orders/{order_id}",
				headers={"Authorization": f"Bearer {token}"},
				timeout=Config.REQUEST_TIMEOUT,
			)
		except Exception:
			pass

	def _simulate_kitchen(
		self, order_id: str, kitchen_token: str
	) -> None:
		"""Simulate kitchen preparing the order."""
		try:
			# Wait a bit before starting preparation
			time.sleep(random.uniform(1, 3))

			# Mark as Preparing
			start = time.time()
			requests.patch(
				f"{self.base_url}/kitchen/orders/{order_id}/status",
				json={"status": "Preparing"},
				headers={
					"Authorization": f"Bearer {kitchen_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			elapsed_ms = (time.time() - start) * 1000
			with self.lock:
				self.results["api_response_times"].append(elapsed_ms)

			# Simulate preparation time
			prep_time = random.uniform(
				Config.KITCHEN_PREP_MIN,
				Config.KITCHEN_PREP_MAX,
			)
			time.sleep(prep_time)

			# Mark as Ready
			start = time.time()
			requests.patch(
				f"{self.base_url}/kitchen/orders/{order_id}/status",
				json={"status": "Ready"},
				headers={
					"Authorization": f"Bearer {kitchen_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			elapsed_ms = (time.time() - start) * 1000
			with self.lock:
				self.results["api_response_times"].append(elapsed_ms)

		except Exception:
			pass

	def _simulate_delivery(
		self, order_id: str, runner_token: str
	) -> None:
		"""Simulate runner delivering the order."""
		statuses = ["PickedUp", "OnTheWay", "Delivered"]

		for status in statuses:
			try:
				# Wait between status updates
				delay = random.uniform(
					Config.RUNNER_DELIVERY_MIN / 3,
					Config.RUNNER_DELIVERY_MAX / 3,
				)
				time.sleep(delay)

				start = time.time()
				requests.patch(
					f"{self.base_url}/runner/deliveries"
					f"/{order_id}/status",
					json={"status": status},
					headers={
						"Authorization": f"Bearer {runner_token}"
					},
					timeout=Config.REQUEST_TIMEOUT,
				)
				elapsed_ms = (time.time() - start) * 1000
				with self.lock:
					self.results["api_response_times"].append(
						elapsed_ms
					)

			except Exception:
				pass

	def _print_results(self) -> None:
		"""Print simulation results."""
		r = self.results

		print("\n" + "=" * 60)
		print("  ORDER FLOW SIMULATION RESULTS")
		print("=" * 60)
		print(f"\n  Total Orders:        {r['total_orders']}")
		print(f"  Successful:          {r['successful']}")
		print(f"  Failed:              {r['failed']}")
		print(f"  Cancelled:           {r['cancelled']}")

		success_rate = (
			(r["successful"] / r["total_orders"] * 100)
			if r["total_orders"] > 0
			else 0
		)
		print(f"  Success Rate:        {success_rate:.1f}%")

		print(f"\n  API Response Times:")
		print(f"    Average:           "
			  f"{r.get('avg_response_time_ms', 0):.1f}ms")
		print(f"    Min:               "
			  f"{r.get('min_response_time_ms', 0):.1f}ms")
		print(f"    Max:               "
			  f"{r.get('max_response_time_ms', 0):.1f}ms")
		print(f"    P50 (median):      "
			  f"{r.get('p50_response_ms', 0):.1f}ms")
		print(f"    P95:               "
			  f"{r.get('p95_response_ms', 0):.1f}ms")
		print(f"    P99:               "
			  f"{r.get('p99_response_ms', 0):.1f}ms")

		if r.get("avg_delivery_time_min"):
			print(f"\n  Avg Delivery Time:   "
				  f"{r['avg_delivery_time_min']:.1f} seconds")

		print(f"\n  Total Elapsed Time:  "
			  f"{r.get('total_time_seconds', 0):.1f}s")

		if r["errors"]:
			print(f"\n  Errors ({len(r['errors'])} total):")
			for error in r["errors"][:10]:
				print(f"    - {error}")
			if len(r["errors"]) > 10:
				print(f"    ... and {len(r['errors']) - 10} more")

		print("=" * 60)


if __name__ == "__main__":
	simulator = OrderFlowSimulator()
	simulator.run(
		num_engineers=10,
		orders_per_engineer=5,
		max_workers=5,
	)
