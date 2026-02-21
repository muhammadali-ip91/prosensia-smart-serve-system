"""
Load Testing Configuration
============================
Central configuration for all load testing and simulation scripts.

All configurable parameters are defined here so they can be
easily modified without changing the actual scripts.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
	"""Main configuration class for automation scripts."""

	# =============================================
	# API Connection Settings
	# =============================================
	BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
	WEBSOCKET_URL = os.getenv("WS_BASE_URL", "ws://localhost:8000")

	# =============================================
	# Simulation Scale Settings
	# =============================================
	TOTAL_ENGINEERS = int(os.getenv("SIM_ENGINEERS", "100"))
	TOTAL_RUNNERS = int(os.getenv("SIM_RUNNERS", "10"))
	TOTAL_KITCHEN_STAFF = int(os.getenv("SIM_KITCHEN", "5"))
	ORDERS_PER_ENGINEER = int(os.getenv("SIM_ORDERS_PER_ENG", "10"))
	TOTAL_STATIONS = int(os.getenv("SIM_STATIONS", "50"))

	# =============================================
	# Timing Settings (seconds)
	# =============================================
	ORDER_INTERVAL_MIN = float(os.getenv("SIM_ORDER_INT_MIN", "2"))
	ORDER_INTERVAL_MAX = float(os.getenv("SIM_ORDER_INT_MAX", "8"))
	KITCHEN_PREP_MIN = float(os.getenv("SIM_PREP_MIN", "3"))
	KITCHEN_PREP_MAX = float(os.getenv("SIM_PREP_MAX", "15"))
	RUNNER_DELIVERY_MIN = float(os.getenv("SIM_DELIVERY_MIN", "2"))
	RUNNER_DELIVERY_MAX = float(os.getenv("SIM_DELIVERY_MAX", "10"))
	REQUEST_TIMEOUT = int(os.getenv("SIM_TIMEOUT", "30"))

	# =============================================
	# Order Distribution Settings
	# =============================================
	URGENT_ORDER_PERCENTAGE = int(
		os.getenv("SIM_URGENT_PCT", "20")
	)
	MAX_ITEMS_PER_ORDER = int(os.getenv("SIM_MAX_ITEMS", "5"))
	CANCELLATION_RATE = float(
		os.getenv("SIM_CANCEL_RATE", "0.05")
	)  # 5% orders get cancelled

	# =============================================
	# Concurrency Settings
	# =============================================
	MAX_CONCURRENT_REQUESTS = int(
		os.getenv("SIM_MAX_CONCURRENT", "50")
	)
	THREAD_POOL_SIZE = int(os.getenv("SIM_THREAD_POOL", "20"))

	# =============================================
	# Authentication Settings
	# =============================================
	ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@prosensia.com")
	ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
	DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "test123")

	# =============================================
	# Menu Items (for simulation)
	# =============================================
	MENU_ITEMS = [
		{
			"id": 1, "name": "Samosa", "price": 20,
			"prep_time": 5, "complexity": 1, "category": "Snacks"
		},
		{
			"id": 2, "name": "Biryani", "price": 120,
			"prep_time": 15, "complexity": 3, "category": "Main Course"
		},
		{
			"id": 3, "name": "Chai", "price": 15,
			"prep_time": 3, "complexity": 1, "category": "Beverages"
		},
		{
			"id": 4, "name": "Sandwich", "price": 50,
			"prep_time": 8, "complexity": 2, "category": "Snacks"
		},
		{
			"id": 5, "name": "Dosa", "price": 60,
			"prep_time": 10, "complexity": 2, "category": "Main Course"
		},
		{
			"id": 6, "name": "Paratha", "price": 40,
			"prep_time": 12, "complexity": 2, "category": "Main Course"
		},
		{
			"id": 7, "name": "Fresh Juice", "price": 35,
			"prep_time": 4, "complexity": 1, "category": "Beverages"
		},
		{
			"id": 8, "name": "Thali", "price": 150,
			"prep_time": 20, "complexity": 3, "category": "Main Course"
		},
		{
			"id": 9, "name": "Pasta", "price": 80,
			"prep_time": 12, "complexity": 2, "category": "Main Course"
		},
		{
			"id": 10, "name": "Coffee", "price": 25,
			"prep_time": 4, "complexity": 1, "category": "Beverages"
		},
	]

	# =============================================
	# Station Definitions
	# =============================================
	BUILDINGS = ["Building-A", "Building-B", "Building-C"]
	FLOORS = [1, 2, 3]

	# =============================================
	# Peak Hour Definitions
	# =============================================
	PEAK_HOURS = [(12, 14), (18, 20)]
	OFF_PEAK_HOURS = [(9, 12), (14, 18)]
	ALL_WORKING_HOURS = [(9, 20)]

	# =============================================
	# Report Settings
	# =============================================
	REPORT_DIR = os.path.join(
		os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
		"reports"
	)

	# =============================================
	# Trivia Questions Count
	# =============================================
	TOTAL_TRIVIA_QUESTIONS = int(
		os.getenv("SIM_TRIVIA_QUESTIONS", "200")
	)

	@classmethod
	def get_stations(cls) -> list:
		"""Generate list of station IDs."""
		return [f"Bay-{i}" for i in range(1, cls.TOTAL_STATIONS + 1)]

	@classmethod
	def is_peak_hour(cls, hour: int) -> bool:
		"""Check if given hour is peak hour."""
		for start, end in cls.PEAK_HOURS:
			if start <= hour < end:
				return True
		return False

	@classmethod
	def print_config(cls):
		"""Print current configuration."""
		print("=" * 50)
		print("  AUTOMATION CONFIGURATION")
		print("=" * 50)
		print(f"  Base URL:          {cls.BASE_URL}")
		print(f"  Engineers:         {cls.TOTAL_ENGINEERS}")
		print(f"  Runners:           {cls.TOTAL_RUNNERS}")
		print(f"  Kitchen Staff:     {cls.TOTAL_KITCHEN_STAFF}")
		print(f"  Orders/Engineer:   {cls.ORDERS_PER_ENGINEER}")
		print(f"  Total Orders:      "
			  f"{cls.TOTAL_ENGINEERS * cls.ORDERS_PER_ENGINEER}")
		print(f"  Stations:          {cls.TOTAL_STATIONS}")
		print(f"  Urgent %:          {cls.URGENT_ORDER_PERCENTAGE}%")
		print(f"  Max Concurrent:    {cls.MAX_CONCURRENT_REQUESTS}")
		print("=" * 50)
