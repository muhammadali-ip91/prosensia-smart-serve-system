"""Runner Business Logic Service"""

from sqlalchemy.orm import Session
from typing import List
from loguru import logger

from models.order_model import Order
from models.runner_model import Runner
from utils.constants import OrderStatus, RunnerStatus
from services.order_service import update_order_status

from fastapi import HTTPException, status


def reconcile_runner_workloads(db: Session):
	"""Recalculate runner active loads from active orders to prevent stale capacity state."""

	runners = db.query(Runner).all()
	for runner in runners:
		active_count = db.query(Order).filter(
			Order.runner_id == runner.runner_id,
			Order.status.in_(OrderStatus.ACTIVE)
		).count()

		runner.active_order_count = active_count

		if runner.current_status != RunnerStatus.OFFLINE:
			if active_count >= runner.max_capacity * 0.8:
				runner.current_status = RunnerStatus.BUSY
			elif runner.current_status == RunnerStatus.BUSY and active_count == 0:
				runner.current_status = RunnerStatus.AVAILABLE

	db.flush()


def get_runner_deliveries(db: Session, runner_id: str) -> dict:
	"""Get all deliveries assigned to a runner"""

	reconcile_runner_workloads(db)

	runner = db.query(Runner).filter(Runner.runner_id == runner_id).first()

	active = db.query(Order).filter(
		Order.runner_id == runner_id,
		Order.status.in_([
			OrderStatus.CONFIRMED, OrderStatus.PREPARING,
			OrderStatus.READY, OrderStatus.PICKED_UP, OrderStatus.ON_THE_WAY
		])
	).order_by(Order.priority.desc(), Order.created_at.asc()).all()

	completed_today = db.query(Order).filter(
		Order.runner_id == runner_id,
		Order.status == OrderStatus.DELIVERED
	).count()

	return {
		"active_deliveries": [o.to_dict() for o in active],
		"active_count": len(active),
		"completed_today": completed_today,
		"current_status": runner.current_status if runner else RunnerStatus.OFFLINE,
	}


def update_delivery_status(db: Session, order_id: str,
						   new_status: str, runner_id: str) -> Order:
	"""Runner updates delivery status"""

	allowed = [OrderStatus.PICKED_UP, OrderStatus.ON_THE_WAY, OrderStatus.DELIVERED]

	if new_status not in allowed:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={
				"code": "ORD_003",
				"message": f"Runner can only set status to: {', '.join(allowed)}"
			}
		)

	# Verify runner is assigned to this order
	order = db.query(Order).filter(Order.order_id == order_id).first()
	if not order:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "ORD_001", "message": "Order not found"}
		)

	if order.runner_id != runner_id:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail={"code": "AUTH_003", "message": "This order is not assigned to you"}
		)

	order = update_order_status(
		db=db,
		order_id=order_id,
		new_status=new_status,
		changed_by=runner_id,
		notes=f"Status updated by runner {runner_id}"
	)

	# If delivered, decrease runner load
	if new_status == OrderStatus.DELIVERED:
		decrease_runner_load(db, runner_id)

	return order


def update_runner_availability(db: Session, runner_id: str, new_status: str) -> Runner:
	"""Update runner's availability status"""

	runner = db.query(Runner).filter(Runner.runner_id == runner_id).first()

	if not runner:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "RUN_001", "message": "Runner not found"}
		)

	if new_status not in RunnerStatus.ALL:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "RUN_001", "message": f"Invalid status: {new_status}"}
		)

	old_status = runner.current_status
	runner.current_status = new_status

	# If going offline, reassign pending orders
	if new_status == RunnerStatus.OFFLINE and old_status != RunnerStatus.OFFLINE:
		reassign_runner_orders(db, runner_id)

	db.commit()
	db.refresh(runner)

	logger.info(f"Runner {runner_id}: {old_status} -> {new_status}")

	return runner


def assign_waiting_ready_orders_to_runner(db: Session, runner_id: str) -> List[Order]:
	"""Assign waiting ready-for-pickup orders to a specific available runner."""

	reconcile_runner_workloads(db)

	runner = db.query(Runner).filter(Runner.runner_id == runner_id).first()
	if not runner:
		return []

	if runner.current_status != RunnerStatus.AVAILABLE:
		return []

	available_slots = max(0, runner.max_capacity - runner.active_order_count)
	if available_slots == 0:
		return []

	waiting_ready_orders = db.query(Order).filter(
		Order.status == OrderStatus.READY,
		Order.runner_id.is_(None)
	).order_by(
		Order.priority.desc(),
		Order.created_at.asc()
	).limit(available_slots).all()

	if not waiting_ready_orders:
		return []

	for order in waiting_ready_orders:
		order.runner_id = runner.runner_id
		runner.active_order_count += 1

	if runner.active_order_count >= runner.max_capacity * 0.8:
		runner.current_status = RunnerStatus.BUSY

	db.commit()

	logger.info(
		f"Assigned {len(waiting_ready_orders)} waiting ready order(s) to runner {runner.runner_id}"
	)

	for order in waiting_ready_orders:
		db.refresh(order)

	return waiting_ready_orders


def assign_waiting_ready_orders(db: Session) -> List[Order]:
	"""Assign all possible waiting ready orders to runners with remaining capacity."""

	reconcile_runner_workloads(db)

	waiting_ready_orders = db.query(Order).filter(
		Order.status == OrderStatus.READY,
		Order.runner_id.is_(None)
	).order_by(
		Order.priority.desc(),
		Order.created_at.asc()
	).all()

	if not waiting_ready_orders:
		return []

	eligible_runners = db.query(Runner).filter(
		Runner.current_status != RunnerStatus.OFFLINE,
		Runner.active_order_count < Runner.max_capacity
	).all()

	if not eligible_runners:
		return []

	assigned_orders: List[Order] = []

	for order in waiting_ready_orders:
		eligible_with_capacity = [
			runner for runner in eligible_runners
			if runner.active_order_count < runner.max_capacity
		]
		if not eligible_with_capacity:
			break

		best_runner = min(
			eligible_with_capacity,
			key=lambda runner: (
				runner.active_order_count / max(runner.max_capacity, 1),
				runner.active_order_count,
			)
		)

		order.runner_id = best_runner.runner_id
		best_runner.active_order_count += 1
		if best_runner.active_order_count >= best_runner.max_capacity * 0.8:
			best_runner.current_status = RunnerStatus.BUSY

		assigned_orders.append(order)

	if assigned_orders:
		db.commit()
		for order in assigned_orders:
			db.refresh(order)
		logger.info(f"Assigned {len(assigned_orders)} waiting ready order(s) from backlog")

	return assigned_orders


def decrease_runner_load(db: Session, runner_id: str):
	"""Decrease runner's active order count"""

	runner = db.query(Runner).filter(Runner.runner_id == runner_id).first()

	if runner:
		runner.active_order_count = max(0, runner.active_order_count - 1)
		runner.total_deliveries += 1

		# Auto set available if no more orders
		if runner.active_order_count == 0 and runner.current_status == RunnerStatus.BUSY:
			runner.current_status = RunnerStatus.AVAILABLE

		db.flush()


def reassign_runner_orders(db: Session, runner_id: str):
	"""Reassign orders when runner goes offline"""

	pending_orders = db.query(Order).filter(
		Order.runner_id == runner_id,
		Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.PREPARING])
	).all()

	from services.runner_assignment_service import assign_optimal_runner

	for order in pending_orders:
		new_runner = assign_optimal_runner(db, order.priority, order.station_id)

		if new_runner:
			order.runner_id = new_runner.runner_id
			logger.info(
				f"Order {order.order_id} reassigned: "
				f"{runner_id} -> {new_runner.runner_id}"
			)
		else:
			logger.warning(f"No runner available to reassign order {order.order_id}")

	db.flush()

