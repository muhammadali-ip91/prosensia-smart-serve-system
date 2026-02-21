"""Authentication Dependencies for FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from auth.jwt_handler import verify_token
from database.session import get_db
from models.user_model import User
from loguru import logger

# Security scheme
security = HTTPBearer()


async def get_current_user(
	credentials: HTTPAuthorizationCredentials = Depends(security),
	db: Session = Depends(get_db)
) -> User:
	"""
	Get current authenticated user from JWT token.
	Use as dependency in protected endpoints.
	"""

	token = credentials.credentials

	# Verify token
	payload = verify_token(token)
	if payload is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail={
				"code": "AUTH_002",
				"message": "Token is invalid or expired"
			}
		)

	# Check token type
	if payload.get("type") != "access":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail={
				"code": "AUTH_002",
				"message": "Invalid token type"
			}
		)

	# Get user from database
	user_id = payload.get("user_id")
	if not user_id:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail={
				"code": "AUTH_002",
				"message": "Invalid token payload"
			}
		)

	user = db.query(User).filter(User.user_id == user_id).first()

	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail={
				"code": "AUTH_001",
				"message": "User not found"
			}
		)

	if not user.is_active:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail={
				"code": "AUTH_004",
				"message": "Account is deactivated"
			}
		)

	return user

