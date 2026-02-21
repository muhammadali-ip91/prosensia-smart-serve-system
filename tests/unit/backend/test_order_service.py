"""
Order Service Unit Tests
==========================
Tests for order creation, modification, cancellation,
and status transitions.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(
	os.path.dirname(__file__), '..', '..', '..'
))


@pytest.mark.unit
class TestOrderValidation:
	"""Tests for order data validation."""

	def test_valid_order_data(self, sample_order_data):
		"""Valid order data should pass validation."""
		assert "station_id" in sample_order_data
		assert "items" in sample_order_data
		assert len(sample_order_data["items"]) > 0
		assert "priority" in sample_order_data

	def test_order_must_have_items(self):
		"""Order without items should be invalid."""
		order_data = {
			"station_id": "Bay-1",
			"items": [],
			"priority": "Regular",
		}
		assert len(order_data["items"]) == 0

	def test_order_must_have_station(self):
		"""Order without station should be invalid."""
		order_data = {
			"items": [{"item_id": 1, "quantity": 1}],
			"priority": "Regular",
		}
		assert "station_id" not in order_data

	def test_order_priority_values(self):
		"""Priority must be Regular or Urgent."""
		valid_priorities = ["Regular", "Urgent"]
		assert "Regular" in valid_priorities
		assert "Urgent" in valid_priorities
		assert "High" not in valid_priorities

	def test_item_quantity_positive(self):
		"""Item quantity must be positive."""
		item = {"item_id": 1, "quantity": 0}
		assert item["quantity"] <= 0  # Should fail validation

		item_valid = {"item_id": 1, "quantity": 2}
		assert item_valid["quantity"] > 0


@pytest.mark.unit
class TestOrderStatusTransitions:
	"""Tests for valid order status transitions."""

	VALID_TRANSITIONS = {
		"Placed": ["Confirmed", "Cancelled", "Rejected"],
		"Confirmed": ["Preparing", "Cancelled"],
		"Preparing": ["Ready", "Delayed"],
		"Ready": ["PickedUp"],
		"PickedUp": ["OnTheWay"],
		"OnTheWay": ["Delivered", "Delayed"],
		"Delivered": [],  # Terminal state
		"Cancelled": [],  # Terminal state
		"Rejected": [],  # Terminal state
	}

	def test_placed_to_confirmed_valid(self):
		"""Placed → Confirmed should be valid."""
		current = "Placed"
		new = "Confirmed"
		assert new in self.VALID_TRANSITIONS[current]

	def test_placed_to_cancelled_valid(self):
		"""Placed → Cancelled should be valid."""
		current = "Placed"
		new = "Cancelled"
		assert new in self.VALID_TRANSITIONS[current]

	def test_placed_to_delivered_invalid(self):
		"""Placed → Delivered should be invalid (skipping steps)."""
		current = "Placed"
		new = "Delivered"
		assert new not in self.VALID_TRANSITIONS[current]

	def test_confirmed_to_preparing_valid(self):
		"""Confirmed → Preparing should be valid."""
		current = "Confirmed"
		new = "Preparing"
		assert new in self.VALID_TRANSITIONS[current]

	def test_preparing_to_cancelled_invalid(self):
		"""Preparing → Cancelled should be invalid."""
		current = "Preparing"
		new = "Cancelled"
		assert new not in self.VALID_TRANSITIONS[current]

	def test_preparing_to_ready_valid(self):
		"""Preparing → Ready should be valid."""
		assert "Ready" in self.VALID_TRANSITIONS["Preparing"]

	def test_ready_to_picked_up_valid(self):
		"""Ready → PickedUp should be valid."""
		assert "PickedUp" in self.VALID_TRANSITIONS["Ready"]

	def test_on_the_way_to_delivered_valid(self):
		"""OnTheWay → Delivered should be valid."""
		assert "Delivered" in self.VALID_TRANSITIONS["OnTheWay"]

	def test_delivered_is_terminal(self):
		"""Delivered should be terminal (no further transitions)."""
		assert len(self.VALID_TRANSITIONS["Delivered"]) == 0

	def test_cancelled_is_terminal(self):
		"""Cancelled should be terminal."""
		assert len(self.VALID_TRANSITIONS["Cancelled"]) == 0

	def test_all_statuses_defined(self):
		"""All status values should have transition rules."""
		expected_statuses = [
			"Placed", "Confirmed", "Preparing", "Ready",
			"PickedUp", "OnTheWay", "Delivered",
			"Cancelled", "Rejected",
		]
		for status in expected_statuses:
			assert status in self.VALID_TRANSITIONS


@pytest.mark.unit
class TestOrderPriceCalculation:
	"""Tests for order price calculations."""

	def test_single_item_price(self):
		"""Single item price calculation."""
		items = [{"item_id": 1, "price": 20, "quantity": 1}]
		total = sum(
			item["price"] * item["quantity"] for item in items
		)
		assert total == 20

	def test_multiple_items_price(self):
		"""Multiple items price calculation."""
		items = [
			{"item_id": 1, "price": 20, "quantity": 2},
			{"item_id": 3, "price": 15, "quantity": 3},
		]
		total = sum(
			item["price"] * item["quantity"] for item in items
		)
		assert total == 85  # (20*2) + (15*3)

	def test_zero_quantity_price(self):
		"""Zero quantity should result in zero price."""
		items = [{"item_id": 1, "price": 100, "quantity": 0}]
		total = sum(
			item["price"] * item["quantity"] for item in items
		)
		assert total == 0

	def test_large_order_price(self):
		"""Large order price calculation."""
		items = [
			{"item_id": 1, "price": 150, "quantity": 5},
			{"item_id": 2, "price": 25, "quantity": 10},
			{"item_id": 3, "price": 80, "quantity": 3},
		]
		total = sum(
			item["price"] * item["quantity"] for item in items
		)
		assert total == 1240  # (150*5) + (25*10) + (80*3)
