"""
Seed Stations Script
======================
Generates factory workstation data.

Usage:
	python -m automation.data_generation.seed_stations
"""

import sys
import os
import random
import hashlib
import requests
from datetime import datetime, timedelta
from typing import List, Dict

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


def generate_station_data(count: int = None) -> List[Dict]:
	"""
	Generate workstation data.
    
	Args:
		count: Number of stations. Defaults to Config.TOTAL_STATIONS.
    
	Returns:
		List of station data dictionaries.
	"""
	if count is None:
		count = Config.TOTAL_STATIONS

	stations = []

	for i in range(1, count + 1):
		building = random.choice(Config.BUILDINGS)
		floor = random.choice(Config.FLOORS)

		# Distance from kitchen varies by building and floor
		base_distance = {
			"Building-A": 50,
			"Building-B": 150,
			"Building-C": 250,
		}.get(building, 100)

		floor_addition = (floor - 1) * 30
		random_variation = random.randint(-20, 50)
		distance = max(
			30,
			base_distance + floor_addition + random_variation
		)

		# Generate encrypted QR token
		token_raw = f"Bay-{i}-{datetime.now().isoformat()}-secret"
		qr_token = hashlib.sha256(
			token_raw.encode()
		).hexdigest()[:32]

		station = {
			"station_id": f"Bay-{i}",
			"station_name": f"Workstation Bay-{i}",
			"floor": floor,
			"building": building,
			"distance_from_kitchen": distance,
			"qr_token": qr_token,
			"qr_token_expires_at": (
				datetime.now() + timedelta(days=1)
			).isoformat(),
			"is_active": True,
		}
		stations.append(station)

	return stations


def seed_stations_via_api(
	base_url: str = None,
	admin_token: str = None,
) -> Dict:
	"""Seed stations via API."""
	if base_url is None:
		base_url = Config.BASE_URL

	stations = generate_station_data()
	print(f"Seeding {len(stations)} stations...")

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
			return {"success": 0, "failed": len(stations)}

	results = {
		"total": len(stations),
		"success": 0,
		"failed": 0,
	}

	for station in stations:
		try:
			response = requests.post(
				f"{base_url}/admin/stations",
				json=station,
				headers={
					"Authorization": f"Bearer {admin_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code in (200, 201, 409):
				results["success"] += 1
			else:
				results["failed"] += 1
		except Exception:
			results["failed"] += 1

	print(f"Stations: ✅ {results['success']} ❌ {results['failed']}")
	return results


if __name__ == "__main__":
	print("=" * 50)
	print("  ProSensia - Seed Stations")
	print("=" * 50)

	stations = generate_station_data()
	print(f"\n{'Station':10s} {'Building':15s} "
		  f"{'Floor':>5s} {'Distance':>10s}")
	print("-" * 45)
	for s in stations[:10]:
		print(
			f"{s['station_id']:10s} {s['building']:15s} "
			f"{s['floor']:>5d} {s['distance_from_kitchen']:>8d}m"
		)
	print(f"... and {len(stations) - 10} more")
	print(f"\nTotal: {len(stations)} stations")
