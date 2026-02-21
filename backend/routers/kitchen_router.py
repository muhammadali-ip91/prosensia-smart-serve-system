"""Kitchen Dashboard Router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from auth.rbac import require_kitchen
from models.user_model import User

from schemas.kitchen_schema import (
    KitchenStatusUpdateRequest,
    MenuAvailabilityRequest,
    KitchenHoursUpdateRequest,
    KitchenToggleRequest,
)
from services.kitchen_service import get_kitchen_orders, update_kitchen_order_status
from services.runner_service import assign_waiting_ready_orders
from services.menu_service import toggle_availability
from services.kitchen_settings_service import (
    get_kitchen_status,
    update_kitchen_hours,
    set_kitchen_force_closed,
)
from websocket.socket_manager import (
    emit_order_update,
    emit_order_update_to_runner,
    emit_order_update_to_kitchen,
)

router = APIRouter()


@router.get("/orders")
async def kitchen_orders(
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """Get all active orders for kitchen"""
    assign_waiting_ready_orders(db)
    return get_kitchen_orders(db)


@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    request: KitchenStatusUpdateRequest,
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """Update order preparation status"""

    order = update_kitchen_order_status(
        db=db,
        order_id=order_id,
        new_status=request.status,
        staff_id=current_user.user_id
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
        "message": f"Order status updated to {order.status}"
    }


@router.patch("/menu/{item_id}/availability")
async def update_item_availability(
    item_id: int,
    request: MenuAvailabilityRequest,
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """Toggle menu item availability"""

    item = toggle_availability(db, item_id, request.available, request.reason)

    return {
        "item_id": item.item_id,
        "item_name": item.item_name,
        "is_available": item.is_available,
        "message": f"{item.item_name} is now {'available' if item.is_available else 'unavailable'}"
    }


@router.get("/settings")
async def kitchen_settings(
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """Get kitchen open/close status and operating hours"""
    return get_kitchen_status(db)


@router.patch("/settings/hours")
async def kitchen_hours(
    request: KitchenHoursUpdateRequest,
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """Update kitchen operating hours"""
    result = update_kitchen_hours(db, request.open_hour, request.close_hour)
    return {
        **result,
        "message": f"Kitchen hours updated to {result['open_hour']:02d}:00 - {result['close_hour']:02d}:00"
    }


@router.patch("/settings/toggle")
async def toggle_kitchen(
    request: KitchenToggleRequest,
    current_user: User = Depends(require_kitchen),
    db: Session = Depends(get_db)
):
    """One-click kitchen close/open toggle"""
    result = set_kitchen_force_closed(
        db,
        force_closed=request.force_closed,
        apply_to_all_menu=request.apply_to_all_menu,
    )
    return {
        **result,
        "message": "Kitchen closed" if request.force_closed else "Kitchen opened"
    }
