"""Order Management Router"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database.session import get_db
from auth.dependencies import get_current_user
from auth.rbac import require_engineer

from models.user_model import User
from schemas.order_schema import (
    CreateOrderRequest, OrderCreateResponse,
    ModifyOrderRequest, FeedbackRequest
)

from services.order_service import (
    create_order, get_order, get_engineer_orders, cancel_order
)
from services.runner_service import assign_waiting_ready_orders
from services.feedback_service import submit_feedback
from websocket.socket_manager import (
    emit_new_order_to_kitchen,
    emit_new_delivery_to_runner,
)

router = APIRouter()


@router.post("", response_model=OrderCreateResponse, status_code=201)
async def place_order(
    request: CreateOrderRequest,
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Place a new order"""

    result = create_order(
        db=db,
        engineer_id=current_user.user_id,
        station_id=request.station_id,
        items=request.items,
        priority=request.priority,
        special_instructions=request.special_instructions
    )

    await emit_new_order_to_kitchen(result)
    if result.get("assigned_runner"):
        await emit_new_delivery_to_runner(result["assigned_runner"], result)

    return result


@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details"""

    assign_waiting_ready_orders(db)

    order = get_order(db, order_id)

    # Check access: owner, assigned runner, kitchen, or admin
    if current_user.role == "engineer" and order.engineer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AUTH_003", "message": "Access denied"}
        )

    if current_user.role == "runner" and order.runner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AUTH_003", "message": "Access denied"}
        )

    return order.to_dict()


@router.get("")
async def get_my_orders(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Get order history for logged-in engineer"""

    return get_engineer_orders(db, current_user.user_id, page, per_page)


@router.delete("/{order_id}")
async def cancel_my_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an order"""

    order = get_order(db, order_id)

    # Verify ownership (unless admin)
    if current_user.role != "admin" and order.engineer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AUTH_003", "message": "Access denied"}
        )

    return cancel_order(db, order_id, current_user.user_id)


@router.post("/{order_id}/feedback")
async def submit_order_feedback(
    order_id: str,
    request: FeedbackRequest,
    current_user: User = Depends(require_engineer),
    db: Session = Depends(get_db)
):
    """Submit feedback for a delivered order"""

    feedback = submit_feedback(
        db=db,
        order_id=order_id,
        engineer_id=current_user.user_id,
        rating=request.rating,
        comment=request.comment
    )

    return {
        "feedback_id": feedback.feedback_id,
        "message": "Feedback submitted successfully"
    }
