"""Order Business Logic Service"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import Optional, List
from loguru import logger

from models.order_model import Order
from models.order_item_model import OrderItem
from models.menu_item_model import MenuItem
from models.order_status_history_model import OrderStatusHistory
from models.notification_model import Notification

from utils.id_generator import generate_order_id
from utils.constants import OrderStatus, STATUS_TRANSITIONS
from utils.validators import validate_priority, validate_kitchen_hours
from utils.helpers import calculate_time_difference_minutes

from services.runner_assignment_service import assign_optimal_runner
from services.eta_service import eta_service
from services.notification_service import create_notification

from fastapi import HTTPException, status


def create_order(db: Session, engineer_id: str, station_id: str,
				 items: list, priority: str, special_instructions: str = None) -> dict:
	"""Create a new order"""

	# Validate kitchen hours
	validate_kitchen_hours(db)

	# Validate priority
	validate_priority(priority)

	# Generate order ID
	order_id = generate_order_id(db)

	# Validate items and calculate total
	total_price = 0.0
	order_items = []

	for item_data in items:
		menu_item = db.query(MenuItem).filter(
			MenuItem.item_id == item_data.item_id
		).first()

		if not menu_item:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={
					"code": "ORD_001",
					"message": f"Menu item with ID {item_data.item_id} not found"
				}
			)

		if not menu_item.is_available:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={
					"code": "ORD_002",
					"message": f"{menu_item.item_name} is currently unavailable",
					"details": {
						"item_id": menu_item.item_id,
						"item_name": menu_item.item_name,
						"reason": menu_item.unavailable_reason or "Out of stock"
					}
				}
			)

		subtotal = menu_item.price * item_data.quantity
		total_price += subtotal

		order_items.append({
			"item_id": menu_item.item_id,
			"quantity": item_data.quantity,
			"item_price": menu_item.price,
			"subtotal": subtotal,
			"menu_item": menu_item
		})

	# Check for duplicate order (within 30 seconds)
	recent_order = db.query(Order).filter(
		and_(
			Order.engineer_id == engineer_id,
			Order.station_id == station_id,
			Order.status == OrderStatus.PLACED,
		)
	).first()

	if recent_order:
		time_diff = calculate_time_difference_minutes(
			recent_order.created_at, datetime.utcnow()
		)
		if time_diff < 1:  # Within 1 minute
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={
					"code": "ORD_005",
					"message": "Duplicate order detected. Please wait before placing another order.",
					"details": {"existing_order_id": recent_order.order_id}
				}
			)

	# Get AI prediction
	prediction = eta_service.predict(
		db=db,
		station_id=station_id,
		items=order_items,
		priority=priority
	)
	predicted_eta = prediction.get("predicted_eta_minutes")
	if predicted_eta is not None:
		predicted_eta = int(round(predicted_eta))

	# Assign runner
	runner = assign_optimal_runner(db, priority, station_id)
	runner_id = runner.runner_id if runner else None

	# Create order
	order = Order(
		order_id=order_id,
		engineer_id=engineer_id,
		station_id=station_id,
		priority=priority,
		status=OrderStatus.PLACED,
		runner_id=runner_id,
		special_instructions=special_instructions,
		total_price=total_price,
		ai_predicted_eta=predicted_eta
	)
	db.add(order)

	# Create order items
	for item in order_items:
		order_item = OrderItem(
			order_id=order_id,
			item_id=item["item_id"],
			quantity=item["quantity"],
			item_price=item["item_price"],
			subtotal=item["subtotal"]
		)
		db.add(order_item)

	# Create status history
	history = OrderStatusHistory(
		order_id=order_id,
		old_status=None,
		new_status=OrderStatus.PLACED,
		changed_by=engineer_id,
		notes="Order placed by engineer"
	)
	db.add(history)

	# Create notification for kitchen
	create_notification(
		db=db,
		user_id=None,  # Will notify all kitchen staff
		notification_type="new_order",
		title="New Order Received!",
		message=f"Order {order_id} from {station_id} - Priority: {priority}",
		priority="high" if priority == "Urgent" else "normal",
		action_url=f"/kitchen/orders/{order_id}",
		role_target="kitchen"
	)

	db.commit()

	logger.info(f"Order {order_id} created by {engineer_id} at {station_id}")

	return {
		"order_id": order_id,
		"status": OrderStatus.PLACED,
		"estimated_wait_time": predicted_eta,
		"eta_confidence": prediction.get("confidence_score"),
		"eta_source": prediction.get("source"),
		"eta_factors": prediction.get("factors"),
		"assigned_runner": runner_id,
		"total_price": total_price,
		"message": "Order placed successfully"
	}


def get_order(db: Session, order_id: str) -> Order:
	"""Get order by ID"""

	order = db.query(Order).filter(Order.order_id == order_id).first()

	if not order:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={
				"code": "ORD_001",
				"message": f"Order {order_id} not found"
			}
		)

	return order


def get_engineer_orders(db: Session, engineer_id: str,
						page: int = 1, per_page: int = 20) -> dict:
	"""Get all orders for an engineer with pagination"""

	query = db.query(Order).filter(
		Order.engineer_id == engineer_id
	).order_by(Order.created_at.desc())

	total = query.count()
	orders = query.offset((page - 1) * per_page).limit(per_page).all()

	return {
		"orders": [order.to_dict() for order in orders],
		"total_count": total,
		"page": page,
		"per_page": per_page,
		"total_pages": (total + per_page - 1) // per_page
	}


def cancel_order(db: Session, order_id: str, user_id: str, reason: str = None) -> dict:
	"""Cancel an order"""

	order = get_order(db, order_id)

	if order.status not in OrderStatus.CANCELLABLE:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_004",
				"message": f"Cannot cancel order in '{order.status}' status. "
						   f"Can only cancel when status is: {', '.join(OrderStatus.CANCELLABLE)}"
			}
		)

	old_status = order.status
	order.status = OrderStatus.CANCELLED
	order.cancelled_reason = reason or "Cancelled by user"
	order.updated_at = datetime.utcnow()

	# Status history
	history = OrderStatusHistory(
		order_id=order_id,
		old_status=old_status,
		new_status=OrderStatus.CANCELLED,
		changed_by=user_id,
		notes=reason or "Cancelled by user"
	)
	db.add(history)

	# Free up runner
	if order.runner_id:
		from services.runner_service import decrease_runner_load
		decrease_runner_load(db, order.runner_id)

	db.commit()

	logger.info(f"Order {order_id} cancelled by {user_id}")

	return {"message": f"Order {order_id} cancelled successfully"}


def update_order_status(db: Session, order_id: str, new_status: str,
						changed_by: str, notes: str = None) -> Order:
	"""Update order status with validation"""

	order = get_order(db, order_id)
	old_status = order.status

	# Validate transition
	if old_status in STATUS_TRANSITIONS:
		allowed = STATUS_TRANSITIONS[old_status]["allowed_next"]
		if new_status not in allowed:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={
					"code": "ORD_003",
					"message": f"Cannot change status from '{old_status}' to '{new_status}'. "
							   f"Allowed: {', '.join(allowed)}"
				}
			)
	else:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_003",
				"message": f"Order in '{old_status}' status cannot be modified"
			}
		)

	# Update order
	order.status = new_status
	order.updated_at = datetime.utcnow()

	# If delivered, record actual delivery time
	if new_status == OrderStatus.DELIVERED:
		order.delivered_at = datetime.utcnow()
		order.actual_delivery_time = calculate_time_difference_minutes(
			order.created_at, datetime.utcnow()
		)

		# Log AI training data
		from services.eta_service import log_training_data
		log_training_data(db, order)

	# Status history
	history = OrderStatusHistory(
		order_id=order_id,
		old_status=old_status,
		new_status=new_status,
		changed_by=changed_by,
		notes=notes
	)
	db.add(history)

	db.commit()

	logger.info(f"Order {order_id}: {old_status} -> {new_status} by {changed_by}")

	return order

