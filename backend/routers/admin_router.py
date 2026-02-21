"""Admin Panel Router"""

from fastapi import APIRouter, Depends, Query, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pathlib import Path
import uuid

from database.session import get_db
from auth.rbac import require_admin
from models.user_model import User

from schemas.menu_schema import CreateMenuItemRequest, UpdateMenuItemRequest
from schemas.auth_schema import RegisterRequest, UpdateUserRequest

from services.analytics_service import get_dashboard_stats, get_popular_items
from services.menu_service import create_menu_item, update_menu_item, delete_menu_item
from services.admin_service import get_all_users, create_user, update_user, toggle_user_active

router = APIRouter()


@router.get("/dashboard")
async def admin_dashboard(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard overview"""
    return get_dashboard_stats(db)


@router.get("/popular-items")
async def popular_items(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get most popular menu items"""
    return get_popular_items(db, limit)


# -------- Menu Management --------

@router.post("/menu")
async def add_menu_item(
    request: CreateMenuItemRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add new menu item"""
    item = create_menu_item(db, request.dict())
    return {"item_id": item.item_id, "message": f"{item.item_name} added successfully"}


@router.post("/menu/upload-image")
async def upload_menu_image(
    image: UploadFile = File(...),
    current_user: User = Depends(require_admin),
):
    """Upload menu item image and return public URL"""

    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MENU_001", "message": "Only image files are allowed"}
        )

    data = await image.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "MENU_002", "message": "Image size must be <= 5MB"}
        )

    extension = Path(image.filename or "").suffix.lower()
    if extension not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        extension = ".jpg"

    filename = f"{uuid.uuid4().hex}{extension}"
    upload_dir = Path(__file__).resolve().parent.parent / "uploads" / "menu"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / filename

    with open(file_path, "wb") as file_obj:
        file_obj.write(data)

    return {
        "image_url": f"/uploads/menu/{filename}",
        "message": "Image uploaded successfully"
    }


@router.put("/menu/{item_id}")
async def edit_menu_item(
    item_id: int,
    request: UpdateMenuItemRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update menu item"""
    item = update_menu_item(db, item_id, request.dict(exclude_unset=True))
    return {"item_id": item.item_id, "message": f"{item.item_name} updated successfully"}


@router.delete("/menu/{item_id}")
async def remove_menu_item(
    item_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete menu item"""
    return delete_menu_item(db, item_id)


# -------- User Management --------

@router.get("/users")
async def list_users(
    role: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users"""
    users = get_all_users(db, role)
    return {"users": [u.to_dict() for u in users], "total": len(users)}


@router.post("/users")
async def add_user(
    request: RegisterRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new user"""
    user = create_user(db, request.dict())
    return {"user_id": user.user_id, "message": f"User {user.name} created successfully"}


@router.put("/users/{user_id}/toggle")
async def toggle_user(
    user_id: str,
    active: bool = True,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Activate/deactivate user"""
    user = toggle_user_active(db, user_id, active)
    status_text = "activated" if active else "deactivated"
    return {"user_id": user.user_id, "message": f"User {status_text}"}


@router.put("/users/{user_id}")
async def edit_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update existing user details"""
    user = update_user(db, user_id, request.dict(exclude_unset=True))
    return {"user_id": user.user_id, "message": f"User {user.name} updated successfully"}
