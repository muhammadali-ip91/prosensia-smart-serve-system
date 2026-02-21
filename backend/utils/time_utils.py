"""Time-related Utility Functions"""

from datetime import datetime
from utils.constants import PEAK_HOURS


def is_peak_hour(hour: int = None) -> bool:
	"""Check if given hour falls in peak hours"""
	if hour is None:
		hour = datetime.now().hour

	for start, end in PEAK_HOURS:
		if start <= hour < end:
			return True

	return False


def get_current_hour() -> int:
	"""Get current hour (0-23)"""
	return datetime.now().hour


def get_current_day_of_week() -> int:
	"""Get current day of week (0=Monday, 6=Sunday)"""
	return datetime.now().weekday()

