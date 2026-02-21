"""
Seed Runners Script
=====================
Generates runner (delivery person) accounts.

Usage:
	python -m automation.data_generation.seed_runners
"""

import sys
import os
import random
import requests
from typing import List, Dict

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config

RUNNER_NAMES = [
	"Raju Kumar", "Sunil Yadav", "Mohan Singh", "Prakash Verma",
	"Dinesh Sharma", "Santosh Gupta", "Manoj Patel", "Vijay Das",
	"Ramesh Thakur", "Anil Joshi", "Pappu Mishra", "Gopal Reddy",
	"Suresh Nair", "Kishore Shah", "Babu Rao",
]


def generate_runner_data(count: int = None) -> List[Dict]:
	"""Generate runner account data."""
	if count is None:
		count = Config.TOTAL_RUNNERS

	runners = []
	for i in range(1, count + 1):
		name = (
			RUNNER_NAMES[i - 1]
			if i <= len(RUNNER_NAMES)
			else f"Runner-{i}"
		)

		runner = {
			"user_id": f"RUN-{i:03d}",
			"name": name,
			"email": f"runner{i}@prosensia.com",
			"password": Config.DEFAULT_PASSWORD,
			"role": "runner",
			"department": "Delivery",
			"phone": f"+91{random.randint(7000000000, 9999999999)}",
		}
		runners.append(runner)

		# Runner extended info
		runner["runner_info"] = {
			"runner_id": f"RUN-{i:03d}",
			"current_status": "Available",
			"active_order_count": 0,
			"max_capacity": random.choice([4, 5, 5, 6]),
			"current_location": "Kitchen Area",
			"total_deliveries": 0,
			"average_delivery_time": 0,
		}

	return runners


def seed_runners_via_api(
	base_url: str = None,
	admin_token: str = None,
) -> Dict:
	"""Seed runners via API."""
	if base_url is None:
		base_url = Config.BASE_URL

	runners = generate_runner_data()
	print(f"Seeding {len(runners)} runners...")

	if admin_token is None:
		try:
			response = requests.post(
				f"{base_url}/auth/login",
				json={
					"employee_id": "ADM-001",
					"password": Config.ADMIN_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			admin_token = response.json()["access_token"]
		except Exception as e:
			print(f"Admin login failed: {e}")
			return {"success": 0, "failed": len(runners)}

	results = {"total": len(runners), "success": 0, "failed": 0}

	for runner in runners:
		try:
			# Create user account
			user_data = {k: v for k, v in runner.items()
						if k != "runner_info"}
			response = requests.post(
				f"{base_url}/admin/users",
				json=user_data,
				headers={
					"Authorization": f"Bearer {admin_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code in (200, 201, 409):
				results["success"] += 1
				print(f"  ✅ {runner['name']}")
			else:
				results["failed"] += 1
				print(f"  ❌ {runner['name']}: {response.status_code}")
		except Exception as e:
			results["failed"] += 1
			print(f"  ❌ {runner['name']}: {str(e)}")

	print(f"\nRunners: ✅ {results['success']} ❌ {results['failed']}")
	return results


if __name__ == "__main__":
	print("=" * 50)
	print("  ProSensia - Seed Runners")
	print("=" * 50)

	runners = generate_runner_data()
	for r in runners:
		info = r.get("runner_info", {})
		print(
			f"  {r['user_id']} | {r['name']:20s} | "
			f"Capacity: {info.get('max_capacity', 5)}"
		)
