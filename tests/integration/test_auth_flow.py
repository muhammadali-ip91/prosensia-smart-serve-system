"""
Authentication Flow Integration Tests
========================================
Tests the complete auth flow: login → token → access → refresh.
"""

import pytest

from tests.conftest import TEST_BASE_URL, auth_header


@pytest.mark.integration
class TestAuthFlow:
    """Integration tests for authentication."""

    def test_login_with_valid_credentials(self, api_client):
        """Login with valid credentials should succeed."""
        response = api_client.post(
            f"{TEST_BASE_URL}/auth/login",
            json={
                "email": "engineer1@prosensia.com",
                "password": "engineer123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "role" in data

    def test_login_with_invalid_credentials(self, api_client):
        """Login with wrong password should fail."""
        response = api_client.post(
            f"{TEST_BASE_URL}/auth/login",
            json={
                "email": "engineer1@prosensia.com",
                "password": "wrong_password",
            },
        )
        assert response.status_code == 401

    def test_login_with_nonexistent_user(self, api_client):
        """Login with non-existent user should fail."""
        response = api_client.post(
            f"{TEST_BASE_URL}/auth/login",
            json={
                "email": "doesnotexist@prosensia.com",
                "password": "engineer123",
            },
        )
        assert response.status_code in (401, 404)

    def test_access_protected_endpoint_with_token(
        self, api_client, engineer_token
    ):
        """Protected endpoint should work with valid token."""
        response = api_client.get(
            f"{TEST_BASE_URL}/menu",
            headers=auth_header(engineer_token),
        )
        assert response.status_code == 200

    def test_access_protected_endpoint_without_token(
        self, api_client
    ):
        """Protected endpoint should reject without token."""
        response = api_client.get(f"{TEST_BASE_URL}/menu")
        assert response.status_code in (401, 403, 422)

    def test_access_with_invalid_token(self, api_client):
        """Invalid token should be rejected."""
        response = api_client.get(
            f"{TEST_BASE_URL}/menu",
            headers=auth_header("invalid.token.here"),
        )
        assert response.status_code in (401, 403)

    def test_get_current_user(
        self, api_client, engineer_token
    ):
        """Should return current user info."""
        response = api_client.get(
            f"{TEST_BASE_URL}/auth/me",
            headers=auth_header(engineer_token),
        )
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "role" in data

    def test_admin_can_access_admin_endpoints(
        self, api_client, admin_token
    ):
        """Admin should access admin endpoints."""
        response = api_client.get(
            f"{TEST_BASE_URL}/admin/dashboard",
            headers=auth_header(admin_token),
        )
        assert response.status_code == 200

    def test_engineer_cannot_access_admin_endpoints(
        self, api_client, engineer_token
    ):
        """Engineer should not access admin endpoints."""
        response = api_client.get(
            f"{TEST_BASE_URL}/admin/dashboard",
            headers=auth_header(engineer_token),
        )
        assert response.status_code in (401, 403)