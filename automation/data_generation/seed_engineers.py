"""
Seed Engineers Script
======================
Generates fake engineer accounts and registers them via API.

Creates realistic engineer data including:
- Employee IDs (ENG-001 to ENG-100)
- Names, emails, departments
- Assigned stations

Usage:
	python -m automation.data_generation.seed_engineers
"""

import sys
import os
import requests
import random
from typing import List, Dict

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config

# Realistic Indian names for engineers
FIRST_NAMES = [
	"Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun",
	"Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
	"Ananya", "Diya", "Aanya", "Aadhya", "Pihu",
	"Saanvi", "Myra", "Sara", "Ira", "Navya",
	"Rahul", "Amit", "Priya", "Neha", "Suresh",
	"Rajesh", "Pooja", "Sneha", "Vikram", "Deepak",
	"Ankita", "Rohit", "Megha", "Karan", "Simran",
	"Manish", "Swati", "Nikhil", "Kavita", "Gaurav",
	"Ritu", "Ashish", "Pallavi", "Sanjay", "Divya",
	"Harsh", "Shruti", "Ajay", "Nisha", "Varun",
]

LAST_NAMES = [
	"Sharma", "Verma", "Patel", "Singh", "Kumar",
	"Gupta", "Mehta", "Joshi", "Shah", "Reddy",
	"Nair", "Pillai", "Iyer", "Rao", "Desai",
	"Kulkarni", "Jain", "Agarwal", "Mishra", "Pandey",
	"Bhat", "Chopra", "Malhotra", "Kapoor", "Banerjee",
	"Das", "Mukherjee", "Ghosh", "Sen", "Thakur",
]

DEPARTMENTS = [
	"Assembly Line", "Quality Control", "Packaging",
	"Maintenance", "Testing Lab", "R&D",
	"Production Floor A", "Production Floor B",
	"Welding Bay", "CNC Operations",
	"Electronics Assembly", "Paint Shop",
	"Logistics", "Inspection Unit", "Tool Room",
]


def generate_engineer_data(count: int = None) -> List[Dict]:
	"""
	Generate engineer account data.
    
	Args:
		count: Number of engineers to generate.
			   Defaults to Config.TOTAL_ENGINEERS.
    
	Returns:
		List of engineer data dictionaries.
	"""
	if count is None:
		count = Config.TOTAL_ENGINEERS

	engineers = []
	stations = Config.get_stations()
	used_names = set()

	for i in range(1, count + 1):
		# Generate unique name
		while True:
			first = random.choice(FIRST_NAMES)
			last = random.choice(LAST_NAMES)
			full_name = f"{first} {last}"
			if full_name not in used_names:
				used_names.add(full_name)
				break

		engineer = {
			"user_id": f"ENG-{i:03d}",
			"name": full_name,
			"email": f"{first.lower()}.{last.lower()}{i}@prosensia.com",
			"password": Config.DEFAULT_PASSWORD,
			"role": "engineer",
			"department": random.choice(DEPARTMENTS),
			"phone": f"+91{random.randint(7000000000, 9999999999)}",
			"station_id": random.choice(stations),
		}
		engineers.append(engineer)

	return engineers


def seed_engineers_via_api(
	engineers: List[Dict] = None,
	base_url: str = None,
) -> Dict:
	"""
	Register engineers via the API.
    
	Args:
		engineers: List of engineer data. Generated if None.
		base_url: API base URL.
    
	Returns:
		Dictionary with success/failure counts.
	"""
	if base_url is None:
		base_url = Config.BASE_URL

	if engineers is None:
		engineers = generate_engineer_data()

	print(f"Seeding {len(engineers)} engineers via API...")
	print(f"API URL: {base_url}")

	# First login as admin to get token
	admin_token = _get_admin_token(base_url)

	results = {
		"total": len(engineers),
		"success": 0,
		"failed": 0,
		"already_exists": 0,
		"errors": [],
	}

	for i, engineer in enumerate(engineers):
		try:
			response = requests.post(
				f"{base_url}/admin/users",
				json=engineer,
				headers={
					"Authorization": f"Bearer {admin_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)

			if response.status_code == 201:
				results["success"] += 1
			elif response.status_code == 409:
				# User already exists
				results["already_exists"] += 1
			else:
				results["failed"] += 1
				results["errors"].append({
					"user_id": engineer["user_id"],
					"status": response.status_code,
					"message": response.text[:200],
				})

		except requests.exceptions.RequestException as e:
			results["failed"] += 1
			results["errors"].append({
				"user_id": engineer["user_id"],
				"error": str(e),
			})

		# Progress update
		if (i + 1) % 20 == 0:
			print(
				f"  Progress: {i + 1}/{len(engineers)} "
				f"(✅ {results['success']} "
				f"⚠️ {results['already_exists']} "
				f"❌ {results['failed']})"
			)

	print(f"\nEngineers seeding complete:")
	print(f"  ✅ Created:       {results['success']}")
	print(f"  ⚠️  Already exist: {results['already_exists']}")
	print(f"  ❌ Failed:        {results['failed']}")

	return results


def seed_engineers_direct(
	engineers: List[Dict] = None,
) -> List[Dict]:
	"""
	Return engineer data without calling API.
	Useful when seeding directly into database.
    
	Returns:
		List of engineer data dictionaries.
	"""
	if engineers is None:
		engineers = generate_engineer_data()

	print(f"Generated {len(engineers)} engineer records")
	return engineers


def _get_admin_token(base_url: str) -> str:
	"""Login as admin and get JWT token."""
	try:
		response = requests.post(
			f"{base_url}/auth/login",
			json={
				"employee_id": "ADM-001",
				"password": Config.ADMIN_PASSWORD,
			},
			timeout=Config.REQUEST_TIMEOUT,
		)
		if response.status_code == 200:
			return response.json()["access_token"]
		else:
			print(
				f"Admin login failed: {response.status_code}"
			)
			# Try with email
			response = requests.post(
				f"{base_url}/auth/login",
				json={
					"email": Config.ADMIN_EMAIL,
					"password": Config.ADMIN_PASSWORD,
				},
				timeout=Config.REQUEST_TIMEOUT,
			)
			if response.status_code == 200:
				return response.json()["access_token"]
			raise Exception(
				f"Admin login failed: {response.text}"
			)
	except requests.exceptions.ConnectionError:
		raise Exception(
			f"Cannot connect to API at {base_url}. "
			f"Is the server running?"
		)


if __name__ == "__main__":
	print("=" * 50)
	print("  ProSensia - Seed Engineers")
	print("=" * 50)

	engineers = generate_engineer_data()

	print(f"\nGenerated {len(engineers)} engineers")
	print("\nSample records:")
	for eng in engineers[:5]:
		print(
			f"  {eng['user_id']} | {eng['name']:20s} | "
			f"{eng['department']:20s} | {eng['station_id']}"
		)

	print(f"\n... and {len(engineers) - 5} more")

	# Uncomment to actually seed via API:
	# seed_engineers_via_api(engineers)
