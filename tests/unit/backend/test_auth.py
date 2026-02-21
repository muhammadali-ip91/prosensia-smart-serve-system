"""
Authentication Unit Tests
===========================
Tests for JWT token creation, verification, password hashing,
and role-based access control.
"""

import pytest
import time
import sys
import os

sys.path.insert(0, os.path.join(
	os.path.dirname(__file__), '..', '..', '..'
))

# Try to import auth modules
try:
	from backend.auth.jwt_handler import (
		create_access_token,
		create_refresh_token,
		verify_token,
	)
	from backend.auth.password_handler import (
		hash_password,
		verify_password,
	)
	from backend.auth.rbac import check_role_permission
	AUTH_MODULES_AVAILABLE = True
except ImportError:
	AUTH_MODULES_AVAILABLE = False


@pytest.mark.unit
class TestPasswordHandler:
	"""Tests for password hashing and verification."""

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_hash_password_returns_hash(self):
		"""Password hashing should return a non-empty hash."""
		password = "test_password_123"
		hashed = hash_password(password)

		assert hashed is not None
		assert len(hashed) > 0
		assert hashed != password  # Hash should differ from original

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_verify_correct_password(self):
		"""Correct password should verify successfully."""
		password = "secure_password_456"
		hashed = hash_password(password)

		assert verify_password(password, hashed) is True

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_verify_incorrect_password(self):
		"""Wrong password should fail verification."""
		password = "secure_password_456"
		wrong_password = "wrong_password_789"
		hashed = hash_password(password)

		assert verify_password(wrong_password, hashed) is False

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_different_hashes_for_same_password(self):
		"""Same password should produce different hashes (salt)."""
		password = "same_password"
		hash1 = hash_password(password)
		hash2 = hash_password(password)

		# Bcrypt uses random salt, so hashes should differ
		assert hash1 != hash2
		# But both should verify correctly
		assert verify_password(password, hash1) is True
		assert verify_password(password, hash2) is True

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_empty_password_handling(self):
		"""Empty password should still be hashable."""
		hashed = hash_password("")
		assert hashed is not None
		assert verify_password("", hashed) is True
		assert verify_password("not_empty", hashed) is False


@pytest.mark.unit
class TestJWTHandler:
	"""Tests for JWT token creation and verification."""

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_create_access_token(self):
		"""Access token should be created successfully."""
		token = create_access_token(
			data={"user_id": "ENG-001", "role": "engineer"}
		)
		assert token is not None
		assert isinstance(token, str)
		assert len(token) > 0

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_verify_valid_token(self):
		"""Valid token should be verified and decoded."""
		user_data = {"user_id": "ENG-001", "role": "engineer"}
		token = create_access_token(data=user_data)

		decoded = verify_token(token)
		assert decoded is not None
		assert decoded["user_id"] == "ENG-001"
		assert decoded["role"] == "engineer"

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_verify_invalid_token(self):
		"""Invalid token should fail verification."""
		result = verify_token("invalid.token.string")
		assert result is None

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_create_refresh_token(self):
		"""Refresh token should be created successfully."""
		token = create_refresh_token(
			data={"user_id": "ENG-001"}
		)
		assert token is not None
		assert isinstance(token, str)

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_different_tokens_for_different_users(self):
		"""Different users should get different tokens."""
		token1 = create_access_token(
			data={"user_id": "ENG-001", "role": "engineer"}
		)
		token2 = create_access_token(
			data={"user_id": "ENG-002", "role": "engineer"}
		)
		assert token1 != token2


@pytest.mark.unit
class TestRBAC:
	"""Tests for role-based access control."""

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_engineer_can_place_order(self):
		"""Engineer should have permission to place orders."""
		result = check_role_permission("engineer", "place_order")
		assert result is True

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_kitchen_cannot_place_order(self):
		"""Kitchen staff should not place orders."""
		result = check_role_permission("kitchen", "place_order")
		assert result is False

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_admin_has_all_permissions(self):
		"""Admin should have all permissions."""
		assert check_role_permission("admin", "place_order") is True
		assert check_role_permission("admin", "manage_menu") is True
		assert check_role_permission("admin", "manage_users") is True
		assert check_role_permission("admin", "view_reports") is True

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_runner_can_update_delivery(self):
		"""Runner should update delivery status."""
		result = check_role_permission(
			"runner", "update_delivery"
		)
		assert result is True

	@pytest.mark.skipif(
		not AUTH_MODULES_AVAILABLE,
		reason="Auth modules not available"
	)
	def test_invalid_role_denied(self):
		"""Invalid role should be denied."""
		result = check_role_permission(
			"invalid_role", "place_order"
		)
		assert result is False
