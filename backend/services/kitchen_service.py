"""Kitchen Business Logic Service"""

from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from models.order_model import Order
from utils.constants import OrderStatus
from services.order_service import update_order_status
from services.runner_assignment_service import assign_optimal_runner


def get_kitchen_orders(db: Session) -> dict:
	"""Get all active orders for kitchen dashboard"""

	# Incoming orders (Placed, Confirmed)
	incoming = db.query(Order).filter(
		Order.status.in_([OrderStatus.PLACED, OrderStatus.CONFIRMED])
	).order_by(
		# Urgent first, then by time
		Order.priority.desc(),
		Order.created_at.asc()
	).all()

	# Currently preparing
	preparing = db.query(Order).filter(
		Order.status == OrderStatus.PREPARING
	).order_by(Order.created_at.asc()).all()

	# Ready for pickup
	ready = db.query(Order).filter(
		Order.status == OrderStatus.READY
	).order_by(Order.created_at.asc()).all()

	return {
		"incoming": [o.to_dict() for o in incoming],
		"preparing": [o.to_dict() for o in preparing],
		"ready": [o.to_dict() for o in ready],
		"counts": {
			"incoming": len(incoming),
			"preparing": len(preparing),
			"ready": len(ready),
			"total_active": len(incoming) + len(preparing) + len(ready)
		}
	}


def update_kitchen_order_status(db: Session, order_id: str,
								 new_status: str, staff_id: str) -> Order:
	"""Kitchen staff updates order status"""

	allowed = [OrderStatus.PREPARING, OrderStatus.READY, OrderStatus.REJECTED]

	if new_status not in allowed:
		from fastapi import HTTPException, status
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_003",
				"message": f"Kitchen can only set status to: {', '.join(allowed)}"
			}
		)

	order = update_order_status(
		db=db,
		order_id=order_id,
		new_status=new_status,
		changed_by=staff_id,
		notes=f"Status updated by kitchen staff {staff_id}"
	)

	# If order is ready but still unassigned, try assigning a runner now.
	if order.status == OrderStatus.READY and not order.runner_id:
		runner = assign_optimal_runner(db, order.priority, order.station_id)
		if runner:
			order.runner_id = runner.runner_id
			db.commit()
			db.refresh(order)
			logger.info(f"Assigned runner {runner.runner_id} to ready order {order.order_id}")

	return order

