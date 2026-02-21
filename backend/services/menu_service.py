"""Menu Business Logic Service"""

from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from models.menu_item_model import MenuItem
from fastapi import HTTPException, status


def get_all_menu_items(db: Session, available_only: bool = False) -> dict:
	"""Get all menu items grouped by category"""

	query = db.query(MenuItem)

	if available_only:
		query = query.filter(MenuItem.is_available == True)

	items = query.order_by(MenuItem.category, MenuItem.item_name).all()

	# Group by category
	categories = {}
	for item in items:
		if item.category not in categories:
			categories[item.category] = []
		categories[item.category].append(item.to_dict())

	result = [
		{"category": cat, "items": items_list}
		for cat, items_list in categories.items()
	]

	return {
		"categories": result,
		"total_items": len(items)
	}


def get_menu_item(db: Session, item_id: int) -> MenuItem:
	"""Get single menu item"""

	item = db.query(MenuItem).filter(MenuItem.item_id == item_id).first()

	if not item:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={
				"code": "ORD_001",
				"message": f"Menu item {item_id} not found"
			}
		)

	return item


def create_menu_item(db: Session, item_data: dict) -> MenuItem:
	"""Create new menu item"""

	item = MenuItem(**item_data)
	db.add(item)
	db.commit()
	db.refresh(item)

	logger.info(f"Menu item created: {item.item_name}")
	return item


def update_menu_item(db: Session, item_id: int, update_data: dict) -> MenuItem:
	"""Update existing menu item"""

	item = get_menu_item(db, item_id)

	for key, value in update_data.items():
		if value is not None:
			setattr(item, key, value)

	db.commit()
	db.refresh(item)

	logger.info(f"Menu item updated: {item.item_name}")
	return item


def toggle_availability(db: Session, item_id: int,
						available: bool, reason: str = None) -> MenuItem:
	"""Toggle menu item availability"""

	item = get_menu_item(db, item_id)
	item.is_available = available
	item.unavailable_reason = reason if not available else None

	db.commit()
	db.refresh(item)

	status_text = "available" if available else "unavailable"
	logger.info(f"Menu item {item.item_name} marked as {status_text}")

	return item


def set_all_menu_availability(db: Session, available: bool, reason: str = None) -> int:
	"""Set availability for all menu items"""

	items = db.query(MenuItem).all()
	for item in items:
		item.is_available = available
		item.unavailable_reason = None if available else reason

	db.commit()

	status_text = "available" if available else "unavailable"
	logger.info(f"All menu items marked as {status_text}. Total: {len(items)}")

	return len(items)


def delete_menu_item(db: Session, item_id: int) -> dict:
	"""Delete a menu item"""

	item = get_menu_item(db, item_id)
	name = item.item_name

	db.delete(item)
	db.commit()

	logger.info(f"Menu item deleted: {name}")
	return {"message": f"Menu item '{name}' deleted successfully"}

