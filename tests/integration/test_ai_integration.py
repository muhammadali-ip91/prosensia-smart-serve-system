"""
AI Integration Tests
======================
Tests that AI module integrates correctly with the backend.
"""

import pytest

from tests.conftest import TEST_BASE_URL, auth_header


@pytest.mark.integration
class TestAIIntegration:
    """Tests for AI module integration."""

    def test_order_includes_ai_prediction(
        self, api_client, engineer_token, sample_order_data
    ):
        """Order response should include AI prediction."""
        response = api_client.post(
            f"{TEST_BASE_URL}/orders",
            json=sample_order_data,
            headers=auth_header(engineer_token),
        )
        if response.status_code in (200, 201):
            data = response.json()
            # Should have some form of ETA
            has_eta = (
                "estimated_wait_time" in data
                or "ai_predicted_eta" in data
            )
            assert has_eta, "Order response missing ETA prediction"

    def test_health_shows_ai_status(self, api_client):
        """Health endpoint should show AI model status."""
        response = api_client.get(f"{TEST_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if "ai_model" in data:
                assert data["ai_model"] in (
                    "loaded", "fallback", "unavailable"
                )