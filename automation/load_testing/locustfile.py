"""
Locust Load Testing Configuration
====================================
Professional-grade load testing using the Locust framework.

Usage:
	locust -f automation/load_testing/locustfile.py
    
Then open http://localhost:8089 in browser to configure
and start the test.
"""

import os
import random
from locust import HttpUser, task, between


ENGINEER_POOL_SIZE = int(os.getenv("LOCUST_ENGINEER_POOL", "100"))
KITCHEN_POOL_SIZE = int(os.getenv("LOCUST_KITCHEN_POOL", "5"))
RUNNER_POOL_SIZE = int(os.getenv("LOCUST_RUNNER_POOL", "10"))
LOGIN_MODE = os.getenv("LOCUST_LOGIN_MODE", "employee_id").lower()
ENGINEER_PASSWORD = os.getenv("LOCUST_ENGINEER_PASSWORD", "engineer123")
KITCHEN_PASSWORD = os.getenv("LOCUST_KITCHEN_PASSWORD", "kitchen123")
RUNNER_PASSWORD = os.getenv("LOCUST_RUNNER_PASSWORD", "runner123")
ENABLE_HEALTH_TASK = os.getenv("LOCUST_ENABLE_HEALTH_TASK", "false").lower() == "true"


def login_payload(user_id: str, password: str, default_email: str = None):
	"""Build login payload for either employee_id or email login mode."""
	if LOGIN_MODE == "email":
		email = default_email or f"{user_id.lower()}@prosensia.com"
		return {"email": email, "password": password}
	return {"employee_id": user_id, "password": password}


class EngineerUser(HttpUser):
	"""Simulates an engineer using the system."""

	wait_time = between(2, 8)
	token = None
	engineer_id = None

	def on_start(self):
		"""Login when user starts."""
		self.engineer_id = (
			f"ENG-{random.randint(1, ENGINEER_POOL_SIZE):03d}"
		)

		response = self.client.post(
			"/auth/login",
			json=login_payload(self.engineer_id, ENGINEER_PASSWORD),
		)

		if response.status_code == 200:
			self.token = response.json().get("access_token")
		else:
			self.token = None

	def _headers(self):
		"""Get auth headers."""
		if self.token:
			return {"Authorization": f"Bearer {self.token}"}
		return {}

	@task(5)
	def view_menu(self):
		"""View menu (most common action)."""
		self.client.get("/menu", headers=self._headers())

	@task(3)
	def place_order(self):
		"""Place a new order."""
		if not self.token:
			return

		items = [
			{
				"item_id": random.randint(1, 10),
				"quantity": random.randint(1, 3),
			}
			for _ in range(random.randint(1, 3))
		]

		self.client.post(
			"/orders",
			json={
				"station_id": f"Bay-{random.randint(1, 50)}",
				"items": items,
				"priority": random.choice([
					"Regular", "Regular", "Regular", "Urgent"
				]),
			},
			headers=self._headers(),
		)

	@task(4)
	def check_orders(self):
		"""Check order history."""
		if not self.token:
			return
		self.client.get(
			"/orders",
			headers=self._headers(),
		)

	@task(1)
	def check_health(self):
		"""Check system health."""
		if not ENABLE_HEALTH_TASK:
			return
		self.client.get("/health")


class KitchenUser(HttpUser):
	"""Simulates kitchen staff."""

	wait_time = between(3, 10)
	token = None
	weight = 2  # Less kitchen users than engineers

	def on_start(self):
		"""Login as kitchen staff."""
		kitchen_id = f"KIT-{random.randint(1, KITCHEN_POOL_SIZE):03d}"
		response = self.client.post(
			"/auth/login",
			json=login_payload(kitchen_id, KITCHEN_PASSWORD),
		)
		if response.status_code == 200:
			self.token = response.json().get("access_token")

	def _headers(self):
		if self.token:
			return {"Authorization": f"Bearer {self.token}"}
		return {}

	@task(3)
	def view_orders(self):
		"""Check incoming orders."""
		if not self.token:
			return
		self.client.get(
			"/kitchen/orders",
			headers=self._headers(),
		)

	@task(1)
	def update_order_status(self):
		"""Update an order status."""
		if not self.token:
			return
		# Get orders first
		response = self.client.get(
			"/kitchen/orders",
			headers=self._headers(),
		)
		if response.status_code == 200:
			data = response.json()
			orders = (
				data if isinstance(data, list)
				else data.get("orders", [])
			)
			if orders:
				order = random.choice(orders)
				order_id = order.get("order_id")
				status = order.get("status")

				new_status = None
				if status in ("Placed", "Confirmed"):
					new_status = "Preparing"
				elif status == "Preparing":
					new_status = "Ready"

				if new_status:
					self.client.patch(
						f"/kitchen/orders/{order_id}/status",
						json={"status": new_status},
						headers=self._headers(),
					)


class RunnerUser(HttpUser):
	"""Simulates delivery runners."""

	wait_time = between(3, 8)
	token = None
	weight = 1  # Even fewer runner users

	def on_start(self):
		"""Login as runner."""
		runner_id = f"RUN-{random.randint(1, RUNNER_POOL_SIZE):03d}"
		response = self.client.post(
			"/auth/login",
			json=login_payload(runner_id, RUNNER_PASSWORD),
		)
		if response.status_code == 200:
			self.token = response.json().get("access_token")

	def _headers(self):
		if self.token:
			return {"Authorization": f"Bearer {self.token}"}
		return {}

	@task(3)
	def check_deliveries(self):
		"""Check assigned deliveries."""
		if not self.token:
			return
		self.client.get(
			"/runner/deliveries",
			headers=self._headers(),
		)

	@task(1)
	def update_delivery(self):
		"""Update delivery status."""
		if not self.token:
			return
		response = self.client.get(
			"/runner/deliveries",
			headers=self._headers(),
		)
		if response.status_code == 200:
			data = response.json()
			deliveries = (
				data if isinstance(data, list)
				else data.get("deliveries", [])
			)
			if deliveries:
				delivery = random.choice(deliveries)
				order_id = delivery.get("order_id")
				status = delivery.get("status")

				new_status = None
				if status == "Ready":
					new_status = "PickedUp"
				elif status == "PickedUp":
					new_status = "OnTheWay"
				elif status == "OnTheWay":
					new_status = "Delivered"

				if new_status:
					self.client.patch(
						f"/runner/deliveries"
						f"/{order_id}/status",
						json={"status": new_status},
						headers=self._headers(),
					)
