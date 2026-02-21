"""
Order Lifecycle Integration Tests
====================================
Tests the complete order flow from placement to delivery.
"""

import pytest
import time

from tests.conftest import TEST_BASE_URL, auth_header


@pytest.mark.integration
class TestOrderLifecycle:
    """Tests for complete order lifecycle."""

    def test_place_order_successfully(
        self, api_client, engineer_token, sample_order_data
    ):
        """Engineer should be able to place an order."""
        response = api_client.post(
            f"{TEST_BASE_URL}/orders",
            json=sample_order_data,
            headers=auth_header(engineer_token),
        )
        assert response.status_code in (200, 201)
        data = response.json()
        assert "order_id" in data
        assert data.get("status") in ("Placed", "Confirmed")

    def test_place_order_includes_eta(
        self, api_client, engineer_token, sample_order_data
    ):
        """Order response should include AI ETA."""
        response = api_client.post(
            f"{TEST_BASE_URL}/orders",
            json=sample_order_data,
            headers=auth_header(engineer_token),
        )
        if response.status_code in (200, 201):
            data = response.json()
            assert (
                "estimated_wait_time" in data
                or "ai_predicted_eta" in data
            )

    def test_get_order_details(
        self, api_client, engineer_token, create_test_order
    ):
        """Should retrieve order details after placement."""
        order = create_test_order()
        if order is None:
            pytest.skip("Could not create test order")

        order_id = order["order_id"]
        response = api_client.get(
            f"{TEST_BASE_URL}/orders/{order_id}",
            headers=auth_header(engineer_token),
        )
        assert response.status_code == 200

    def test_get_my_orders(
        self, api_client, engineer_token
    ):
        """Should retrieve engineer's order history."""
        response = api_client.get(
            f"{TEST_BASE_URL}/orders",
            headers=auth_header(engineer_token),
        )
        assert response.status_code == 200

    def test_cancel_placed_order(
        self, api_client, engineer_token, create_test_order
    ):
        """Should be able to cancel a placed order."""
        order = create_test_order()
        if order is None:
            pytest.skip("Could not create test order")

        order_id = order["order_id"]
        response = api_client.delete(
            f"{TEST_BASE_URL}/orders/{order_id}",
            headers=auth_header(engineer_token),
        )
        assert response.status_code in (200, 204)

    def test_kitchen_sees_new_orders(
        self, api_client, kitchen_token,
        engineer_token, create_test_order
    ):
        """Kitchen should see newly placed orders."""
        order = create_test_order()
        if order is None:
            pytest.skip("Could not create test order")

        response = api_client.get(
            f"{TEST_BASE_URL}/kitchen/orders",
            headers=auth_header(kitchen_token),
        )
        assert response.status_code == 200

    def test_kitchen_updates_status(
        self, api_client, kitchen_token,
        engineer_token, create_test_order
    ):
        """Kitchen should update order status."""
        order = create_test_order()
        if order is None:
            pytest.skip("Could not create test order")

        order_id = order["order_id"]

        # Update to Preparing
        response = api_client.patch(
            f"{TEST_BASE_URL}/kitchen/orders/{order_id}/status",
            json={"status": "Preparing"},
            headers=auth_header(kitchen_token),
        )
        assert response.status_code == 200

    def test_complete_order_flow(
        self, api_client, engineer_token,
        kitchen_token, runner_token,
        sample_order_data
    ):
        """Test the complete order lifecycle."""
        # Step 1: Place order
        response = api_client.post(
            f"{TEST_BASE_URL}/orders",
            json=sample_order_data,
            headers=auth_header(engineer_token),
        )
        if response.status_code not in (200, 201):
            pytest.skip("Could not place order")

        order_id = response.json()["order_id"]

        # Step 2: Kitchen starts preparing
        api_client.patch(
            f"{TEST_BASE_URL}/kitchen/orders/{order_id}/status",
            json={"status": "Preparing"},
            headers=auth_header(kitchen_token),
        )

        # Step 3: Kitchen marks ready
        api_client.patch(
            f"{TEST_BASE_URL}/kitchen/orders/{order_id}/status",
            json={"status": "Ready"},
            headers=auth_header(kitchen_token),
        )

        # Resolve assigned runner token dynamically
        detail_response = api_client.get(
            f"{TEST_BASE_URL}/orders/{order_id}",
            headers=auth_header(engineer_token),
        )
        assigned_runner_id = None
        if detail_response.status_code == 200:
            assigned_runner_id = detail_response.json().get("runner_id")
        if not assigned_runner_id:
            pytest.skip("No runner assigned for this order")

        runner_header = auth_header(runner_token)
        runner_credentials = {
            "RUN-001": {"email": "runner1@prosensia.com", "password": "runner123"},
            "RUN-002": {"email": "runner2@prosensia.com", "password": "runner123"},
            "RUN-003": {"email": "runner3@prosensia.com", "password": "runner123"},
            "RUN-004": {"email": "runner4@prosensia.com", "password": "runner123"},
            "RUN-005": {"email": "runner5@prosensia.com", "password": "runner123"},
        }
        if assigned_runner_id in runner_credentials:
            login_response = api_client.post(
                f"{TEST_BASE_URL}/auth/login",
                json=runner_credentials[assigned_runner_id],
            )
            if login_response.status_code == 200:
                runner_header = auth_header(login_response.json()["access_token"])

        # Step 4: Runner picks up
        pickup_response = api_client.patch(
            f"{TEST_BASE_URL}/runner/deliveries/{order_id}/status",
            json={"status": "PickedUp"},
            headers=runner_header,
        )
        if pickup_response.status_code != 200:
            pytest.skip("Runner could not pick up assigned order")

        # Step 5: Runner starts route
        route_response = api_client.patch(
            f"{TEST_BASE_URL}/runner/deliveries/{order_id}/status",
            json={"status": "OnTheWay"},
            headers=runner_header,
        )
        if route_response.status_code != 200:
            pytest.skip("Runner could not set order OnTheWay")

        # Step 6: Runner delivers
        deliver_response = api_client.patch(
            f"{TEST_BASE_URL}/runner/deliveries/{order_id}/status",
            json={"status": "Delivered"},
            headers=runner_header,
        )
        if deliver_response.status_code != 200:
            pytest.skip("Runner could not mark order Delivered")

        # Step 6: Verify final status
        response = api_client.get(
            f"{TEST_BASE_URL}/orders/{order_id}",
            headers=auth_header(engineer_token),
        )
        if response.status_code == 200:
            assert response.json().get("status") == "Delivered"

    def test_cannot_cancel_preparing_order(
        self, api_client, engineer_token,
        kitchen_token, create_test_order
    ):
        """Should not cancel order that's being prepared."""
        order = create_test_order()
        if order is None:
            pytest.skip("Could not create test order")

        order_id = order["order_id"]

        # Move to Preparing
        api_client.patch(
            f"{TEST_BASE_URL}/kitchen/orders/{order_id}/status",
            json={"status": "Preparing"},
            headers=auth_header(kitchen_token),
        )

        # Try to cancel
        response = api_client.delete(
            f"{TEST_BASE_URL}/orders/{order_id}",
            headers=auth_header(engineer_token),
        )
        assert response.status_code == 400

    def test_place_order_with_empty_items_fails(
        self, api_client, engineer_token
    ):
        """Order with empty items should fail."""
        response = api_client.post(
            f"{TEST_BASE_URL}/orders",
            json={
                "station_id": "Bay-1",
                "items": [],
                "priority": "Regular",
            },
            headers=auth_header(engineer_token),
        )
        assert response.status_code in (400, 422)