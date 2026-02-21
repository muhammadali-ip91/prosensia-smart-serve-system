"""Menu Router"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from auth.dependencies import get_current_user
from models.user_model import User
from services.menu_service import get_all_menu_items

router = APIRouter()


@router.get("")
async def get_menu(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available menu items"""
    return get_all_menu_items(db, available_only=True)


@router.get("/all")
async def get_full_menu(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all menu items (including unavailable)"""
    return get_all_menu_items(db, available_only=False)
