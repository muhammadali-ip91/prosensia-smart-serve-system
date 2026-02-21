"""Kitchen Settings Service"""

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.kitchen_settings_model import KitchenSettings
from services.menu_service import set_all_menu_availability


def _is_within_schedule(open_hour: int, close_hour: int, current_hour: int) -> bool:
	if open_hour == close_hour:
		return False

	if open_hour < close_hour:
		return open_hour <= current_hour < close_hour

	return current_hour >= open_hour or current_hour < close_hour


def get_or_create_kitchen_settings(db: Session) -> KitchenSettings:
	settings = db.query(KitchenSettings).filter(KitchenSettings.id == 1).first()
	if settings:
		return settings

	settings = KitchenSettings(id=1, force_closed=False, open_hour=9, close_hour=21)
	db.add(settings)
	db.commit()
	db.refresh(settings)
	return settings


def get_kitchen_status(db: Session) -> dict:
	settings = get_or_create_kitchen_settings(db)
	current_hour = datetime.now().hour
	within_schedule = _is_within_schedule(settings.open_hour, settings.close_hour, current_hour)
	is_open_now = (not settings.force_closed) and within_schedule

	if settings.force_closed:
		reason = "Manually closed"
	elif not within_schedule:
		reason = "Outside operating hours"
	else:
		reason = "Open"

	return {
		"is_open_now": is_open_now,
		"reason": reason,
		"force_closed": settings.force_closed,
		"open_hour": settings.open_hour,
		"close_hour": settings.close_hour,
		"current_hour": current_hour,
	}


def update_kitchen_hours(db: Session, open_hour: int, close_hour: int) -> dict:
	if open_hour < 0 or open_hour > 23 or close_hour < 0 or close_hour > 23:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "KIT_001", "message": "Hours must be between 0 and 23"}
		)

	settings = get_or_create_kitchen_settings(db)
	settings.open_hour = open_hour
	settings.close_hour = close_hour
	db.commit()
	db.refresh(settings)

	return get_kitchen_status(db)


def set_kitchen_force_closed(db: Session, force_closed: bool, apply_to_all_menu: bool = True) -> dict:
	settings = get_or_create_kitchen_settings(db)
	settings.force_closed = force_closed
	db.commit()
	db.refresh(settings)

	affected_items = 0
	if apply_to_all_menu:
		if force_closed:
			affected_items = set_all_menu_availability(db, available=False, reason="Kitchen closed")
		else:
			affected_items = set_all_menu_availability(db, available=True, reason=None)

	result = get_kitchen_status(db)
	result["affected_items"] = affected_items
	return result
