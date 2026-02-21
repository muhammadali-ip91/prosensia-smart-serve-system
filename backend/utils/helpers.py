"""General Utility Functions"""

from datetime import datetime
from typing import Optional


def get_current_timestamp() -> str:
	"""Get current timestamp as ISO string"""
	return datetime.utcnow().isoformat() + "Z"


def calculate_time_difference_minutes(start: datetime, end: Optional[datetime] = None) -> int:
	"""Calculate difference between two timestamps in minutes"""
	if end is None:
		end = datetime.utcnow()

	diff = end - start
	return int(diff.total_seconds() / 60)


def format_price(price: float) -> str:
	"""Format price to 2 decimal places"""
	return f"Rs. {price:.2f}"

