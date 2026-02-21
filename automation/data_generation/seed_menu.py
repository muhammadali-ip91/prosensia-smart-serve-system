"""
Seed Menu Items Script
========================
Generates and seeds menu items into the system.

Usage:
	python -m automation.data_generation.seed_menu
"""

import sys
import os
import requests
from typing import List, Dict

sys.path.insert(
	0,
	os.path.dirname(os.path.dirname(os.path.dirname(
		os.path.abspath(__file__)
	)))
)

from automation.load_testing.config import Config


MENU_ITEMS_FULL = [
	# Snacks
	{
		"item_name": "Samosa", "category": "Snacks",
		"price": 20, "prep_time_estimate": 5,
		"complexity_score": 1,
		"image_url": "/images/menu/samosa.jpg",
		"is_available": True,
	},
	{
		"item_name": "Vada Pav", "category": "Snacks",
		"price": 25, "prep_time_estimate": 5,
		"complexity_score": 1,
		"image_url": "/images/menu/vadapav.jpg",
		"is_available": True,
	},
	{
		"item_name": "Bread Pakora", "category": "Snacks",
		"price": 30, "prep_time_estimate": 7,
		"complexity_score": 1,
		"image_url": "/images/menu/breadpakora.jpg",
		"is_available": True,
	},
	{
		"item_name": "Pani Puri", "category": "Snacks",
		"price": 30, "prep_time_estimate": 3,
		"complexity_score": 1,
		"image_url": "/images/menu/panipuri.jpg",
		"is_available": True,
	},
	{
		"item_name": "Spring Roll", "category": "Snacks",
		"price": 40, "prep_time_estimate": 8,
		"complexity_score": 2,
		"image_url": "/images/menu/springroll.jpg",
		"is_available": True,
	},

	# Main Course
	{
		"item_name": "Biryani", "category": "Main Course",
		"price": 120, "prep_time_estimate": 15,
		"complexity_score": 3,
		"image_url": "/images/menu/biryani.jpg",
		"is_available": True,
	},
	{
		"item_name": "Dosa", "category": "Main Course",
		"price": 60, "prep_time_estimate": 10,
		"complexity_score": 2,
		"image_url": "/images/menu/dosa.jpg",
		"is_available": True,
	},
	{
		"item_name": "Paratha Plate", "category": "Main Course",
		"price": 50, "prep_time_estimate": 12,
		"complexity_score": 2,
		"image_url": "/images/menu/paratha.jpg",
		"is_available": True,
	},
	{
		"item_name": "Thali", "category": "Main Course",
		"price": 150, "prep_time_estimate": 20,
		"complexity_score": 3,
		"image_url": "/images/menu/thali.jpg",
		"is_available": True,
	},
	{
		"item_name": "Chole Bhature", "category": "Main Course",
		"price": 70, "prep_time_estimate": 12,
		"complexity_score": 2,
		"image_url": "/images/menu/cholebhature.jpg",
		"is_available": True,
	},
	{
		"item_name": "Rajma Chawal", "category": "Main Course",
		"price": 80, "prep_time_estimate": 10,
		"complexity_score": 2,
		"image_url": "/images/menu/rajmachawal.jpg",
		"is_available": True,
	},
	{
		"item_name": "Pasta", "category": "Main Course",
		"price": 80, "prep_time_estimate": 12,
		"complexity_score": 2,
		"image_url": "/images/menu/pasta.jpg",
		"is_available": True,
	},
	{
		"item_name": "Fried Rice", "category": "Main Course",
		"price": 70, "prep_time_estimate": 10,
		"complexity_score": 2,
		"image_url": "/images/menu/friedrice.jpg",
		"is_available": True,
	},
	{
		"item_name": "Sandwich", "category": "Main Course",
		"price": 50, "prep_time_estimate": 8,
		"complexity_score": 2,
		"image_url": "/images/menu/sandwich.jpg",
		"is_available": True,
	},

	# Beverages
	{
		"item_name": "Chai", "category": "Beverages",
		"price": 15, "prep_time_estimate": 3,
		"complexity_score": 1,
		"image_url": "/images/menu/chai.jpg",
		"is_available": True,
	},
	{
		"item_name": "Coffee", "category": "Beverages",
		"price": 25, "prep_time_estimate": 4,
		"complexity_score": 1,
		"image_url": "/images/menu/coffee.jpg",
		"is_available": True,
	},
	{
		"item_name": "Fresh Juice", "category": "Beverages",
		"price": 35, "prep_time_estimate": 4,
		"complexity_score": 1,
		"image_url": "/images/menu/juice.jpg",
		"is_available": True,
	},
	{
		"item_name": "Lassi", "category": "Beverages",
		"price": 30, "prep_time_estimate": 3,
		"complexity_score": 1,
		"image_url": "/images/menu/lassi.jpg",
		"is_available": True,
	},
	{
		"item_name": "Buttermilk", "category": "Beverages",
		"price": 20, "prep_time_estimate": 2,
		"complexity_score": 1,
		"image_url": "/images/menu/buttermilk.jpg",
		"is_available": True,
	},
	{
		"item_name": "Cold Coffee", "category": "Beverages",
		"price": 40, "prep_time_estimate": 5,
		"complexity_score": 1,
		"image_url": "/images/menu/coldcoffee.jpg",
		"is_available": True,
	},
]


def generate_menu_data() -> List[Dict]:
	"""Generate menu item data."""
	return MENU_ITEMS_FULL


def seed_menu_via_api(
	base_url: str = None,
	admin_token: str = None,
) -> Dict:
	"""
	Seed menu items via the API.
    
	Args:
		base_url: API base URL.
		admin_token: Admin JWT token.
    
	Returns:
		Results dictionary.
	"""
	if base_url is None:
		base_url = Config.BASE_URL

	items = generate_menu_data()
	print(f"Seeding {len(items)} menu items...")

	if admin_token is None:
		admin_token = _get_admin_token(base_url)

	results = {"total": len(items), "success": 0, "failed": 0}

	for item in items:
		try:
			response = requests.post(
				f"{base_url}/admin/menu",
				json=item,
				headers={
					"Authorization": f"Bearer {admin_token}"
				},
				timeout=Config.REQUEST_TIMEOUT,
			)

			if response.status_code in (200, 201):
				results["success"] += 1
				print(f"  ✅ {item['item_name']}")
			elif response.status_code == 409:
				results["success"] += 1  # Already exists
				print(f"  ⚠️  {item['item_name']} (exists)")
			else:
				results["failed"] += 1
				print(
					f"  ❌ {item['item_name']}: "
					f"{response.status_code}"
				)

		except Exception as e:
			results["failed"] += 1
			print(f"  ❌ {item['item_name']}: {str(e)}")

	print(f"\nMenu seeding: ✅ {results['success']} "
		  f"❌ {results['failed']}")
	return results


def _get_admin_token(base_url: str) -> str:
	"""Login as admin."""
	response = requests.post(
		f"{base_url}/auth/login",
		json={
			"employee_id": "ADM-001",
			"password": Config.ADMIN_PASSWORD,
		},
		timeout=Config.REQUEST_TIMEOUT,
	)
	return response.json()["access_token"]


if __name__ == "__main__":
	print("=" * 50)
	print("  ProSensia - Seed Menu Items")
	print("=" * 50)

	items = generate_menu_data()
	print(f"\n{'Item Name':20s} {'Category':15s} "
		  f"{'Price':>6s} {'Prep':>5s} {'Cmplx':>5s}")
	print("-" * 55)
	for item in items:
		print(
			f"{item['item_name']:20s} {item['category']:15s} "
			f"₹{item['price']:>4d} {item['prep_time_estimate']:>4d}m "
			f"  {item['complexity_score']}"
		)
	print(f"\nTotal: {len(items)} items")
