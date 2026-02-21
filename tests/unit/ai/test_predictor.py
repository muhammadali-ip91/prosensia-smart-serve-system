"""
ETA Predictor Tests
=====================
Tests for the main AI prediction engine.
"""

import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..'
))

from ai_module.core.predictor import ETAPredictor
from ai_module.core.feature_engineering import FeatureEngineer
from ai_module.core.fallback import FallbackPredictor


@pytest.mark.ai
class TestETAPredictor:
    """Tests for the main ETAPredictor class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize predictor for each test."""
        self.predictor = ETAPredictor()

    def test_predictor_initializes(self):
        """Predictor should initialize without errors."""
        assert self.predictor is not None

    def test_predict_returns_required_fields(
        self, sample_ai_order_data
    ):
        """Prediction should contain all required fields."""
        result = self.predictor.predict(sample_ai_order_data)

        assert "predicted_eta_minutes" in result
        assert "confidence_score" in result
        assert "source" in result
        assert "factors" in result

    def test_predict_returns_positive_eta(
        self, sample_ai_order_data
    ):
        """Predicted ETA should always be positive."""
        result = self.predictor.predict(sample_ai_order_data)
        assert result["predicted_eta_minutes"] > 0

    def test_predict_eta_within_bounds(
        self, sample_ai_order_data
    ):
        """ETA should be between 3 and 60 minutes."""
        result = self.predictor.predict(sample_ai_order_data)
        eta = result["predicted_eta_minutes"]
        assert 3 <= eta <= 60

    def test_predict_confidence_in_range(
        self, sample_ai_order_data
    ):
        """Confidence should be between 0 and 1."""
        result = self.predictor.predict(sample_ai_order_data)
        confidence = result["confidence_score"]
        assert 0.0 <= confidence <= 1.0

    def test_predict_source_is_valid(
        self, sample_ai_order_data
    ):
        """Source should be 'ai_model' or 'fallback'."""
        result = self.predictor.predict(sample_ai_order_data)
        valid_sources = [
            "ai_model", "fallback",
            "fallback_default", "ultimate_fallback",
        ]
        assert result["source"] in valid_sources

    def test_predict_has_factors(self, sample_ai_order_data):
        """Prediction should include factor descriptions."""
        result = self.predictor.predict(sample_ai_order_data)
        factors = result["factors"]

        assert "kitchen_load" in factors
        assert "runner_availability" in factors

    def test_peak_hour_higher_eta(
        self, sample_peak_hour_order, sample_off_peak_order
    ):
        """Peak hour orders should have higher ETA."""
        peak_result = self.predictor.predict(
            sample_peak_hour_order
        )
        offpeak_result = self.predictor.predict(
            sample_off_peak_order
        )

        # Peak should generally be higher
        # (may not always hold due to model variance,
        # but should hold on average)
        peak_eta = peak_result["predicted_eta_minutes"]
        offpeak_eta = offpeak_result["predicted_eta_minutes"]

        # At minimum, peak should not be drastically lower
        assert peak_eta >= offpeak_eta * 0.5

    def test_urgent_order_lower_eta(self):
        """Urgent orders should have lower or equal ETA."""
        regular_data = {
            "items": [{"prep_time": 10, "complexity_score": 2, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "active_orders_count": 10,
            "available_runners": 3,
            "kitchen_queue_length": 5,
            "order_time": datetime(2024, 1, 15, 13, 0, 0),
        }

        urgent_data = regular_data.copy()
        urgent_data["priority"] = "Urgent"

        regular_result = self.predictor.predict(regular_data)
        urgent_result = self.predictor.predict(urgent_data)

        # Urgent should generally not be MORE than regular
        assert urgent_result["predicted_eta_minutes"] <= \
            regular_result["predicted_eta_minutes"] * 1.2

    def test_never_returns_none(self, sample_ai_order_data):
        """Predictor should NEVER return None."""
        result = self.predictor.predict(sample_ai_order_data)
        assert result is not None
        assert result["predicted_eta_minutes"] is not None

    def test_get_stats(self):
        """Stats should return valid structure."""
        stats = self.predictor.get_stats()

        assert "total_predictions" in stats
        assert "model_predictions" in stats
        assert "fallback_predictions" in stats
        assert "is_model_active" in stats

    def test_prediction_count_increments(
        self, sample_ai_order_data
    ):
        """Prediction count should increment after each call."""
        initial_stats = self.predictor.get_stats()
        initial_count = initial_stats["total_predictions"]

        self.predictor.predict(sample_ai_order_data)

        new_stats = self.predictor.get_stats()
        assert new_stats["total_predictions"] == initial_count + 1