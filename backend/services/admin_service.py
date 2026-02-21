"""Admin Business Logic Service"""

from sqlalchemy.orm import Session
from typing import List, Optional
from loguru import logger

from models.user_model import User
from auth.password_handler import hash_password
from utils.validators import validate_role

from fastapi import HTTPException, status


def get_all_users(db: Session, role: Optional[str] = None) -> List[User]:
	"""Get all users, optionally filtered by role"""

	query = db.query(User)

	if role:
		validate_role(role)
		query = query.filter(User.role == role)

	return query.order_by(User.user_id).all()


def create_user(db: Session, user_data: dict) -> User:
	"""Create new user"""

	# Check email uniqueness
	existing = db.query(User).filter(User.email == user_data["email"]).first()
	if existing:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "AUTH_001", "message": "Email already registered"}
		)

	# Check user_id uniqueness
	existing = db.query(User).filter(User.user_id == user_data["user_id"]).first()
	if existing:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail={"code": "AUTH_001", "message": "User ID already exists"}
		)

	# Hash password
	user_data["password_hash"] = hash_password(user_data.pop("password"))

	user = User(**user_data)
	db.add(user)
	db.commit()
	db.refresh(user)

	logger.info(f"User created: {user.user_id} ({user.role})")
	return user


def update_user(db: Session, user_id: str, update_data: dict) -> User:
	"""Update user details"""

	user = db.query(User).filter(User.user_id == user_id).first()

	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "AUTH_001", "message": "User not found"}
		)

	if "role" in update_data and update_data["role"] is not None:
		validate_role(update_data["role"])

	if "email" in update_data and update_data["email"]:
		existing = db.query(User).filter(
			User.email == update_data["email"],
			User.user_id != user_id,
		).first()
		if existing:
			raise HTTPException(
				status_code=status.HTTP_400_BAD_REQUEST,
				detail={"code": "AUTH_001", "message": "Email already registered"}
			)

	for key, value in update_data.items():
		if value is not None and key != "password":
			setattr(user, key, value)

	if "password" in update_data and update_data["password"]:
		user.password_hash = hash_password(update_data["password"])

	db.commit()
	db.refresh(user)

	logger.info(f"User updated: {user.user_id}")
	return user


def toggle_user_active(db: Session, user_id: str, is_active: bool) -> User:
	"""Activate or deactivate user"""

	user = db.query(User).filter(User.user_id == user_id).first()

	if not user:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail={"code": "AUTH_001", "message": "User not found"}
		)

	user.is_active = is_active
	db.commit()
	db.refresh(user)

	status_text = "activated" if is_active else "deactivated"
	logger.info(f"User {user_id} {status_text}")

	return user
