"""
ID Generator Tests
====================
Tests for unique ID generation.
"""

import pytest
import re
from datetime import datetime


@pytest.mark.unit
class TestOrderIDGenerator:
	"""Tests for order ID generation."""

	def generate_order_id(self, sequence: int) -> str:
		"""Simple order ID generator for testing."""
		year = datetime.now().year
		return f"ORD-{year}-{sequence:04d}"

	def test_generates_correct_format(self):
		"""Order ID should follow ORD-YYYY-NNNN format."""
		order_id = self.generate_order_id(1)
		pattern = re.compile(r"^ORD-\d{4}-\d{4}$")
		assert pattern.match(order_id) is not None

	def test_sequential_ids_unique(self):
		"""Sequential IDs should be unique."""
		ids = [self.generate_order_id(i) for i in range(1, 101)]
		assert len(ids) == len(set(ids))

	def test_first_id_is_0001(self):
		"""First order ID should end with 0001."""
		order_id = self.generate_order_id(1)
		assert order_id.endswith("0001")

	def test_id_contains_current_year(self):
		"""Order ID should contain current year."""
		order_id = self.generate_order_id(1)
		current_year = str(datetime.now().year)
		assert current_year in order_id

	def test_padding_works_correctly(self):
		"""Numbers should be zero-padded to 4 digits."""
		assert self.generate_order_id(1).endswith("0001")
		assert self.generate_order_id(10).endswith("0010")
		assert self.generate_order_id(100).endswith("0100")
		assert self.generate_order_id(1000).endswith("1000")
