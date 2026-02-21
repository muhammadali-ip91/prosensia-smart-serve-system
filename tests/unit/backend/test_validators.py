"""
Input Validator Tests
========================
Tests for custom input validation functions.
"""

import pytest
import re


@pytest.mark.unit
class TestStationValidator:
	"""Tests for station ID validation."""

	STATION_PATTERN = re.compile(r"^Bay-\d{1,3}$")

	def test_valid_station_ids(self):
		"""Valid station IDs should pass."""
		valid_ids = ["Bay-1", "Bay-12", "Bay-50", "Bay-100"]
		for sid in valid_ids:
			assert self.STATION_PATTERN.match(sid) is not None

	def test_invalid_station_ids(self):
		"""Invalid station IDs should fail."""
		invalid_ids = [
			"bay-1", "Bay1", "Bay-", "Station-1",
			"", "Bay-1000", "Bay-abc",
		]
		for sid in invalid_ids:
			result = self.STATION_PATTERN.match(sid)
			assert result is None, f"{sid} should be invalid"


@pytest.mark.unit
class TestOrderIDValidator:
	"""Tests for order ID format validation."""

	ORDER_PATTERN = re.compile(r"^ORD-\d{4}-\d{4}$")

	def test_valid_order_ids(self):
		"""Valid order IDs should match pattern."""
		valid = [
			"ORD-2024-0001", "ORD-2024-0100",
			"ORD-2025-9999",
		]
		for oid in valid:
			assert self.ORDER_PATTERN.match(oid) is not None

	def test_invalid_order_ids(self):
		"""Invalid order IDs should not match."""
		invalid = [
			"ORD-2024", "ORD-0001", "order-2024-0001",
			"", "ORD-24-0001",
		]
		for oid in invalid:
			assert self.ORDER_PATTERN.match(oid) is None


@pytest.mark.unit
class TestUserIDValidator:
	"""Tests for user ID format validation."""

	USER_PATTERN = re.compile(
		r"^(ENG|KIT|RUN|ADM)-\d{3}$"
	)

	def test_valid_user_ids(self):
		"""Valid user IDs should match."""
		valid = [
			"ENG-001", "ENG-100", "KIT-001",
			"RUN-010", "ADM-001",
		]
		for uid in valid:
			assert self.USER_PATTERN.match(uid) is not None

	def test_invalid_user_ids(self):
		"""Invalid user IDs should not match."""
		invalid = [
			"eng-001", "ENG001", "ENG-1",
			"ENG-0001", "USR-001", "",
		]
		for uid in invalid:
			assert self.USER_PATTERN.match(uid) is None


@pytest.mark.unit
class TestEmailValidator:
	"""Tests for email validation."""

	EMAIL_PATTERN = re.compile(
		r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
	)

	def test_valid_emails(self):
		"""Valid emails should pass."""
		valid = [
			"user@prosensia.com",
			"test.user@prosensia.com",
			"admin@prosensia.co.in",
		]
		for email in valid:
			assert self.EMAIL_PATTERN.match(email) is not None

	def test_invalid_emails(self):
		"""Invalid emails should fail."""
		invalid = [
			"user", "user@", "@prosensia.com",
			"user @prosensia.com", "",
		]
		for email in invalid:
			assert self.EMAIL_PATTERN.match(email) is None


@pytest.mark.unit
class TestRatingValidator:
	"""Tests for feedback rating validation."""

	def test_valid_ratings(self):
		"""Ratings 1-5 should be valid."""
		for rating in [1, 2, 3, 4, 5]:
			assert 1 <= rating <= 5

	def test_invalid_ratings(self):
		"""Ratings outside 1-5 should be invalid."""
		for rating in [0, -1, 6, 10, 100]:
			assert not (1 <= rating <= 5)


@pytest.mark.unit
class TestTimeUtils:
	"""Tests for time utility functions."""

	PEAK_HOURS = [(12, 14), (18, 20)]

	def is_peak_hour(self, hour: int) -> bool:
		for start, end in self.PEAK_HOURS:
			if start <= hour < end:
				return True
		return False

	def test_lunch_is_peak(self):
		"""12-14 should be peak hours."""
		assert self.is_peak_hour(12) is True
		assert self.is_peak_hour(13) is True

	def test_dinner_is_peak(self):
		"""18-20 should be peak hours."""
		assert self.is_peak_hour(18) is True
		assert self.is_peak_hour(19) is True

	def test_morning_not_peak(self):
		"""Morning should not be peak."""
		assert self.is_peak_hour(9) is False
		assert self.is_peak_hour(10) is False
		assert self.is_peak_hour(11) is False

	def test_afternoon_not_peak(self):
		"""Afternoon (14-18) should not be peak."""
		assert self.is_peak_hour(14) is False
		assert self.is_peak_hour(15) is False
		assert self.is_peak_hour(16) is False

	def test_boundary_hours(self):
		"""Boundary hours should be correctly identified."""
		assert self.is_peak_hour(11) is False  # Just before peak
		assert self.is_peak_hour(12) is True   # Start of peak
		assert self.is_peak_hour(14) is False  # End of peak (exclusive)
		assert self.is_peak_hour(17) is False  # Before dinner peak
		assert self.is_peak_hour(18) is True   # Start of dinner peak
		assert self.is_peak_hour(20) is False  # End of dinner peak
