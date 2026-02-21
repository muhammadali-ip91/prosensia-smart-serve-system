"""
Cleanup load-test users and dependent records.

Usage:
	python -m automation.load_testing.cleanup_load_test_data --prefix ENG-
	python -m automation.load_testing.cleanup_load_test_data --prefix RUN- --apply

By default it runs in dry-run mode.
Use --apply to execute deletion.
"""

import os
import sys
from typing import List

from sqlalchemy import delete, select, or_

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)
if BACKEND_ROOT not in sys.path:
	sys.path.insert(0, BACKEND_ROOT)

from database.connection import SessionLocal
from models.user_model import User
from models.runner_model import Runner
from models.order_model import Order
from models.order_item_model import OrderItem
from models.order_status_history_model import OrderStatusHistory


def cleanup(prefixes: List[str], apply: bool = False) -> dict:
	"""Delete load-test users and dependent data by user_id prefixes."""
	db = SessionLocal()
	try:
		conditions = [User.user_id.like(f"{prefix}%") for prefix in prefixes]
		users = db.execute(select(User.user_id).where(or_(*conditions))).scalars().all()
		user_ids = list(users)

		if not user_ids:
			return {
				"matched_users": 0,
				"deleted_orders": 0,
				"deleted_order_items": 0,
				"deleted_status_history": 0,
				"deleted_runners": 0,
				"deleted_users": 0,
				"applied": apply,
			}

		order_ids = db.execute(
			select(Order.order_id).where(
				(Order.engineer_id.in_(user_ids)) | (Order.runner_id.in_(user_ids))
			)
		).scalars().all()

		result = {
			"matched_users": len(user_ids),
			"deleted_orders": 0,
			"deleted_order_items": 0,
			"deleted_status_history": 0,
			"deleted_runners": 0,
			"deleted_users": 0,
			"applied": apply,
		}

		if not apply:
			result["candidate_order_ids"] = len(order_ids)
			return result

		if order_ids:
			status_deleted = db.execute(
				delete(OrderStatusHistory).where(OrderStatusHistory.order_id.in_(order_ids))
			)
			result["deleted_status_history"] += status_deleted.rowcount or 0

			items_deleted = db.execute(
				delete(OrderItem).where(OrderItem.order_id.in_(order_ids))
			)
			result["deleted_order_items"] += items_deleted.rowcount or 0

		status_by_user_deleted = db.execute(
			delete(OrderStatusHistory).where(OrderStatusHistory.changed_by.in_(user_ids))
		)
		result["deleted_status_history"] += status_by_user_deleted.rowcount or 0

		runner_deleted = db.execute(
			delete(Runner).where(Runner.runner_id.in_(user_ids))
		)
		result["deleted_runners"] = runner_deleted.rowcount or 0

		if order_ids:
			orders_deleted = db.execute(
				delete(Order).where(Order.order_id.in_(order_ids))
			)
			result["deleted_orders"] = orders_deleted.rowcount or 0

		users_deleted = db.execute(
			delete(User).where(User.user_id.in_(user_ids))
		)
		result["deleted_users"] = users_deleted.rowcount or 0

		db.commit()
		return result

	except Exception:
		db.rollback()
		raise
	finally:
		db.close()


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Cleanup load-test data by user_id prefix")
	parser.add_argument("--prefix", action="append", dest="prefixes", default=["ENG-", "RUN-"])
	parser.add_argument("--apply", action="store_true", help="Apply deletion (default is dry-run)")
	args = parser.parse_args()

	res = cleanup(args.prefixes, apply=args.apply)
	print(res)
