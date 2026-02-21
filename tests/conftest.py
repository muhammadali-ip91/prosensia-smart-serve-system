"""
Pytest Fixtures & Configuration
=================================
Shared fixtures used across all test suites.

Provides:
- Test database session
- Test client (FastAPI TestClient)
- Authentication helpers
- Test data factories
- Cleanup utilities
"""

import os
import sys
import pytest
import time
from itertools import count
from typing import Dict, Generator, Optional
from datetime import datetime

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Try to import FastAPI test client
try:
	from fastapi.testclient import TestClient
	from backend.main import app
	BACKEND_AVAILABLE = True
except ImportError:
	BACKEND_AVAILABLE = False

# Try to import database session
try:
	from sqlalchemy import create_engine
	from sqlalchemy.orm import sessionmaker
	DB_AVAILABLE = True
except ImportError:
	DB_AVAILABLE = False

import requests


# =============================================
# Configuration
# =============================================

TEST_BASE_URL = os.getenv("TEST_API_URL", "http://localhost:8000")
TEST_ADMIN_EMAIL = "admin@prosensia.com"
TEST_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
TEST_ENGINEER_EMAIL = "engineer1@prosensia.com"
TEST_ENGINEER_PASSWORD = os.getenv("ENGINEER_PASSWORD", "engineer123")
TEST_KITCHEN_EMAIL = "kitchen1@prosensia.com"
TEST_KITCHEN_PASSWORD = os.getenv("KITCHEN_PASSWORD", "kitchen123")
TEST_RUNNER_EMAIL = "runner1@prosensia.com"
TEST_RUNNER_PASSWORD = os.getenv("RUNNER_PASSWORD", "runner123")

_STATION_COUNTER = count(start=1)


def _next_station_id() -> str:
	return f"Bay-{((next(_STATION_COUNTER) - 1) % 48) + 1}"


# =============================================
# FastAPI Test Client Fixture
# =============================================

@pytest.fixture(scope="session")
def client():
	"""
	FastAPI test client.
	Uses the app directly (no server needed).
	"""
	if BACKEND_AVAILABLE:
		with TestClient(app) as c:
			yield c
	else:
		pytest.skip("Backend not available for direct testing")


@pytest.fixture(scope="session")
def api_client():
	"""
	HTTP client for API testing against running server.
	Requires the server to be running.
	"""
	session = requests.Session()
	session.base_url = TEST_BASE_URL
	session.timeout = 30

	# Check if server is running
	try:
		response = session.get(f"{TEST_BASE_URL}/health", timeout=5)
		if response.status_code != 200:
			pytest.skip("Backend server not healthy")
	except requests.ConnectionError:
		pytest.skip(
			f"Backend server not running at {TEST_BASE_URL}"
		)

	yield session
	session.close()


# =============================================
# Authentication Fixtures
# =============================================

@pytest.fixture(scope="session")
def admin_token(api_client) -> str:
	"""Get admin JWT token."""
	response = api_client.post(
		f"{TEST_BASE_URL}/auth/login",
		json={
			"email": TEST_ADMIN_EMAIL,
			"password": TEST_ADMIN_PASSWORD,
		},
	)
	if response.status_code == 200:
		return response.json()["access_token"]
	pytest.skip("Admin login failed")


@pytest.fixture(scope="session")
def engineer_token(api_client) -> str:
	"""Get engineer JWT token."""
	response = api_client.post(
		f"{TEST_BASE_URL}/auth/login",
		json={
			"email": TEST_ENGINEER_EMAIL,
			"password": TEST_ENGINEER_PASSWORD,
		},
	)
	if response.status_code == 200:
		return response.json()["access_token"]
	pytest.skip("Engineer login failed")


@pytest.fixture(scope="session")
def kitchen_token(api_client) -> str:
	"""Get kitchen staff JWT token."""
	response = api_client.post(
		f"{TEST_BASE_URL}/auth/login",
		json={
			"email": TEST_KITCHEN_EMAIL,
			"password": TEST_KITCHEN_PASSWORD,
		},
	)
	if response.status_code == 200:
		return response.json()["access_token"]
	pytest.skip("Kitchen login failed")


@pytest.fixture(scope="session")
def runner_token(api_client) -> str:
	"""Get runner JWT token."""
	response = api_client.post(
		f"{TEST_BASE_URL}/auth/login",
		json={
			"email": TEST_RUNNER_EMAIL,
			"password": TEST_RUNNER_PASSWORD,
		},
	)
	if response.status_code == 200:
		return response.json()["access_token"]
	pytest.skip("Runner login failed")


def auth_header(token: str) -> Dict[str, str]:
	"""Create authorization header from token."""
	return {"Authorization": f"Bearer {token}"}


# =============================================
# Test Data Factories
# =============================================

@pytest.fixture
def sample_order_data() -> Dict:
	"""Create sample order data for testing."""
	return {
		"station_id": _next_station_id(),
		"items": [
			{"item_id": 1, "quantity": 2},
			{"item_id": 3, "quantity": 1},
		],
		"priority": "Regular",
		"special_instructions": "Test order - less spicy",
	}


@pytest.fixture
def sample_urgent_order_data() -> Dict:
	"""Create sample urgent order data."""
	return {
		"station_id": _next_station_id(),
		"items": [
			{"item_id": 2, "quantity": 1},
		],
		"priority": "Urgent",
		"special_instructions": None,
	}


@pytest.fixture
def sample_user_data() -> Dict:
	"""Create sample user data for registration."""
	timestamp = int(time.time())
	return {
		"user_id": f"ENG-TEST-{timestamp}",
		"name": f"Test Engineer {timestamp}",
		"email": f"test_{timestamp}@prosensia.com",
		"password": TEST_ENGINEER_PASSWORD,
		"role": "engineer",
		"department": "Testing",
		"phone": "+919999999999",
	}


@pytest.fixture
def sample_menu_item_data() -> Dict:
	"""Create sample menu item data."""
	timestamp = int(time.time())
	return {
		"item_name": f"Test Item {timestamp}",
		"category": "Snacks",
		"price": 50.00,
		"prep_time_estimate": 8,
		"complexity_score": 2,
		"image_url": "/images/test.jpg",
		"is_available": True,
	}


@pytest.fixture
def sample_feedback_data() -> Dict:
	"""Create sample feedback data."""
	return {
		"rating": 4,
		"comment": "Test feedback - food was good",
	}


@pytest.fixture
def sample_trivia_answer() -> Dict:
	"""Create sample trivia answer."""
	return {
		"question_id": 1,
		"selected_option": "A",
		"time_taken_seconds": 8,
	}


# =============================================
# AI Module Fixtures
# =============================================

@pytest.fixture
def sample_ai_order_data() -> Dict:
	"""Create sample order data for AI prediction."""
	return {
		"items": [
			{
				"prep_time": 10,
				"complexity_score": 2,
				"quantity": 2,
			},
			{
				"prep_time": 5,
				"complexity_score": 1,
				"quantity": 1,
			},
		],
		"station_distance": 150,
		"priority": "Regular",
		"active_orders_count": 8,
		"available_runners": 3,
		"kitchen_queue_length": 5,
		"order_time": datetime(2024, 1, 15, 13, 30, 0),
	}


@pytest.fixture
def sample_peak_hour_order() -> Dict:
	"""Order data during peak hours."""
	return {
		"items": [
			{
				"prep_time": 15,
				"complexity_score": 3,
				"quantity": 1,
			},
		],
		"station_distance": 200,
		"priority": "Regular",
		"active_orders_count": 20,
		"available_runners": 2,
		"kitchen_queue_length": 15,
		"order_time": datetime(2024, 1, 15, 13, 0, 0),
	}


@pytest.fixture
def sample_off_peak_order() -> Dict:
	"""Order data during off-peak hours."""
	return {
		"items": [
			{
				"prep_time": 3,
				"complexity_score": 1,
				"quantity": 1,
			},
		],
		"station_distance": 50,
		"priority": "Regular",
		"active_orders_count": 3,
		"available_runners": 5,
		"kitchen_queue_length": 1,
		"order_time": datetime(2024, 1, 15, 10, 0, 0),
	}


# =============================================
# Helper Fixtures
# =============================================

@pytest.fixture
def base_url() -> str:
	"""Get test API base URL."""
	return TEST_BASE_URL


@pytest.fixture
def create_test_order(api_client, engineer_token, sample_order_data):
	"""
	Factory fixture to create a test order.
	Returns a function that creates orders.
	"""
	created_order_ids = []

	def _create_order(order_data: Dict = None) -> Dict:
		base_data = dict(order_data or sample_order_data)
		for _ in range(5):
			data = dict(base_data)
			data["station_id"] = _next_station_id()
			response = api_client.post(
				f"{TEST_BASE_URL}/orders",
				json=data,
				headers=auth_header(engineer_token),
			)
			if response.status_code in (200, 201):
				order = response.json()
				created_order_ids.append(order.get("order_id"))
				return order
			if response.status_code != 400:
				break
			try:
				detail = response.json().get("detail", {})
			except Exception:
				detail = {}
			if detail.get("code") != "ORD_005":
				break
		return None

	yield _create_order

	# Cleanup: Cancel any orders created during test
	for order_id in created_order_ids:
		try:
			api_client.delete(
				f"{TEST_BASE_URL}/orders/{order_id}",
				headers=auth_header(engineer_token),
			)
		except Exception:
			pass


# =============================================
# Timing Helper
# =============================================

@pytest.fixture
def timer():
	"""Simple timer for performance measurements."""

	class Timer:
		def __init__(self):
			self.start_time = None
			self.end_time = None

		def start(self):
			self.start_time = time.time()

		def stop(self):
			self.end_time = time.time()

		@property
		def elapsed_ms(self):
			if self.start_time and self.end_time:
				return (self.end_time - self.start_time) * 1000
			return 0

	return Timer()
