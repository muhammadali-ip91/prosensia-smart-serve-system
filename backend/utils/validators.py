"""Custom Input Validators"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from utils.constants import OrderStatus, RunnerStatus, Priority, UserRole
from utils.constants import KITCHEN_OPEN_HOUR, KITCHEN_CLOSE_HOUR
from datetime import datetime

from services.kitchen_settings_service import get_kitchen_status


def validate_order_status(new_status: str):
	"""Validate order status value"""
	if new_status not in OrderStatus.ALL:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_001",
				"message": f"Invalid status: {new_status}. "
						   f"Allowed: {', '.join(OrderStatus.ALL)}"
			}
		)


def validate_runner_status(new_status: str):
	"""Validate runner status value"""
	if new_status not in RunnerStatus.ALL:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "RUN_001",
				"message": f"Invalid runner status: {new_status}. "
						   f"Allowed: {', '.join(RunnerStatus.ALL)}"
			}
		)


def validate_priority(priority: str):
	"""Validate order priority"""
	if priority not in Priority.ALL:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_001",
				"message": f"Invalid priority: {priority}. "
						   f"Allowed: {', '.join(Priority.ALL)}"
			}
		)


def validate_role(role: str):
	"""Validate user role"""
	if role not in UserRole.ALL:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "AUTH_001",
				"message": f"Invalid role: {role}. "
						   f"Allowed: {', '.join(UserRole.ALL)}"
			}
		)


def validate_kitchen_hours(db: Session | None = None):
	"""Check if kitchen is open"""
	if db is not None:
		status_info = get_kitchen_status(db)
		if not status_info["is_open_now"]:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={
					"code": "ORD_006",
					"message": f"Kitchen is closed. Hours: {status_info['open_hour']}:00 AM - {status_info['close_hour']}:00 PM"
				}
			)
		return

	current_hour = datetime.now().hour

	if current_hour < KITCHEN_OPEN_HOUR or current_hour >= KITCHEN_CLOSE_HOUR:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_006",
				"message": f"Kitchen is closed. Hours: {KITCHEN_OPEN_HOUR}:00 AM - {KITCHEN_CLOSE_HOUR}:00 PM"
			}
		)

