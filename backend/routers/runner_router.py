"""Runner Interface Router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from auth.rbac import require_runner
from models.user_model import User

from schemas.runner_schema import RunnerStatusUpdateRequest, RunnerAvailabilityRequest
from services.runner_service import (
    get_runner_deliveries,
    update_delivery_status,
    update_runner_availability,
    assign_waiting_ready_orders_to_runner,
)
from websocket.socket_manager import (
    emit_order_update,
    emit_order_update_to_runner,
    emit_order_update_to_kitchen,
    emit_new_delivery_to_runner,
)

router = APIRouter()


@router.get("/deliveries")
async def my_deliveries(
    current_user: User = Depends(require_runner),
    db: Session = Depends(get_db)
):
    """Get assigned deliveries for runner"""
    assign_waiting_ready_orders_to_runner(db, current_user.user_id)
    return get_runner_deliveries(db, current_user.user_id)


@router.patch("/deliveries/{order_id}/status")
async def update_my_delivery_status(
    order_id: str,
    request: RunnerStatusUpdateRequest,
    current_user: User = Depends(require_runner),
    db: Session = Depends(get_db)
):
    """Update delivery status"""

    order = update_delivery_status(
        db=db,
        order_id=order_id,
        new_status=request.status,
        runner_id=current_user.user_id
    )

    payload = {
        "order_id": order.order_id,
        "old_status": None,
        "new_status": order.status,
        "engineer_id": order.engineer_id,
        "runner_id": order.runner_id,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
    }
    await emit_order_update(order.order_id, order.engineer_id, payload)
    await emit_order_update_to_kitchen(payload)
    if order.runner_id:
        await emit_order_update_to_runner(order.runner_id, payload)

    return {
        "order_id": order.order_id,
        "status": order.status,
        "message": f"Delivery status updated to {order.status}"
    }


@router.patch("/status")
async def update_my_availability(
    request: RunnerAvailabilityRequest,
    current_user: User = Depends(require_runner),
    db: Session = Depends(get_db)
):
    """Update runner availability status"""

    runner = update_runner_availability(
        db=db,
        runner_id=current_user.user_id,
        new_status=request.status
    )

    assigned_orders = []
    if runner.current_status == "Available":
        assigned_orders = assign_waiting_ready_orders_to_runner(db, current_user.user_id)

    for order in assigned_orders:
        payload = {
            "order_id": order.order_id,
            "old_status": None,
            "new_status": order.status,
            "engineer_id": order.engineer_id,
            "runner_id": order.runner_id,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }
        await emit_order_update(order.order_id, order.engineer_id, payload)
        await emit_order_update_to_kitchen(payload)
        await emit_order_update_to_runner(order.runner_id, payload)
        await emit_new_delivery_to_runner(order.runner_id, payload)

    return {
        "runner_id": runner.runner_id,
        "status": runner.current_status,
        "message": (
            f"Status updated to {runner.current_status}"
            + (f". {len(assigned_orders)} waiting order(s) assigned" if assigned_orders else "")
        )
    }
