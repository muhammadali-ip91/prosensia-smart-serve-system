"""JWT Token Creation and Verification"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from config import settings
from loguru import logger


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
	"""Create a JWT access token"""
	to_encode = data.copy()

	if expires_delta:
		expire = datetime.utcnow() + expires_delta
	else:
		expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

	to_encode.update({
		"exp": expire,
		"type": "access"
	})

	encoded_jwt = jwt.encode(
		to_encode,
		settings.JWT_SECRET_KEY,
		algorithm=settings.JWT_ALGORITHM
	)

	return encoded_jwt


def create_refresh_token(data: Dict) -> str:
	"""Create a JWT refresh token"""
	to_encode = data.copy()

	expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

	to_encode.update({
		"exp": expire,
		"type": "refresh"
	})

	encoded_jwt = jwt.encode(
		to_encode,
		settings.JWT_SECRET_KEY,
		algorithm=settings.JWT_ALGORITHM
	)

	return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
	"""Verify and decode a JWT token"""
	try:
		payload = jwt.decode(
			token,
			settings.JWT_SECRET_KEY,
			algorithms=[settings.JWT_ALGORITHM]
		)
		return payload

	except JWTError as e:
		logger.warning(f"JWT verification failed: {e}")
		return None

