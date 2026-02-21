"""Authentication Router"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.session import get_db
from auth.password_handler import verify_password
from auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from auth.dependencies import get_current_user

from models.user_model import User
from schemas.auth_schema import (
    LoginRequest, RegisterRequest, TokenResponse,
    RefreshTokenRequest, UserResponse
)

from loguru import logger

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and get JWT tokens"""

    if not request.email and not request.employee_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "AUTH_005", "message": "email or employee_id is required"}
        )

    user = None

    # Preferred login by email
    if request.email:
        user = db.query(User).filter(User.email == request.email).first()

    # Backward compatibility for automation/legacy clients
    if not user and request.employee_id:
        user = db.query(User).filter(User.user_id == request.employee_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_001", "message": "Invalid email or password"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "AUTH_004", "message": "Account is deactivated"}
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_001", "message": "Invalid email or password"}
        )

    # Create tokens
    token_data = {"user_id": user.user_id, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    logger.info(f"User {user.user_id} logged in successfully")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "user": user.to_dict()
    }


@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""

    payload = verify_token(request.refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_002", "message": "Invalid refresh token"}
        )

    token_data = {"user_id": payload["user_id"], "role": payload["role"]}
    new_access_token = create_access_token(token_data)

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user.to_dict()


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout (client should discard tokens)"""
    logger.info(f"User {current_user.user_id} logged out")
    return {"message": "Logged out successfully"}
