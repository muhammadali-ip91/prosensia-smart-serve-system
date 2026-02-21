"""Notification Router"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database.session import get_db
from auth.dependencies import get_current_user
from models.user_model import User
from schemas.notification_schema import MarkReadRequest

from services.notification_service import (
    get_user_notifications, mark_notifications_read, get_unread_count
)

router = APIRouter()


@router.get("")
async def my_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get my notifications"""

    notifications = get_user_notifications(
        db, current_user.user_id, unread_only, limit
    )

    return {
        "notifications": [n.to_dict() for n in notifications],
        "unread_count": get_unread_count(db, current_user.user_id)
    }


@router.patch("/read")
async def mark_read(
    request: MarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notifications as read"""

    count = mark_notifications_read(
        db, current_user.user_id, request.notification_ids
    )

    return {"marked_read": count}
