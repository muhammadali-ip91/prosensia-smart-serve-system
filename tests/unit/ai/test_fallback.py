"""
Fallback Predictor Tests
==========================
Tests for the rule-based fallback prediction system.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..'
))

from ai_module.core.fallback import FallbackPredictor


@pytest.mark.ai
class TestFallbackPredictor:
    """Tests for the FallbackPredictor class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize fallback predictor."""
        self.predictor = FallbackPredictor()

    def test_returns_required_fields(self):
        """Fallback should return all required fields."""
        data = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 5,
            "available_runners": 3,
            "is_peak_hour": 0,
        }
        result = self.predictor.predict(data)

        assert "predicted_eta_minutes" in result
        assert "confidence_score" in result
        assert "source" in result
        assert "factors" in result

    def test_source_is_fallback(self):
        """Source should always be 'fallback'."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 2,
            "available_runners": 3,
        }
        result = self.predictor.predict(data)
        assert result["source"] in ("fallback", "fallback_default")

    def test_confidence_lower_than_model(self):
        """Fallback confidence should be lower than ML model."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 2,
            "available_runners": 3,
        }
        result = self.predictor.predict(data)
        # Fallback confidence is typically 0.55
        assert result["confidence_score"] < 0.70

    def test_eta_within_bounds(self):
        """ETA should be between 3 and 60 minutes."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 2,
            "available_runners": 3,
        }
        result = self.predictor.predict(data)
        eta = result["predicted_eta_minutes"]
        assert 3 <= eta <= 60

    def test_peak_hour_increases_eta(self):
        """Peak hour should increase ETA."""
        base = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 5,
            "available_runners": 3,
        }

        off_peak = {**base, "is_peak_hour": 0}
        peak = {**base, "is_peak_hour": 1}

        result_off = self.predictor.predict(off_peak)
        result_peak = self.predictor.predict(peak)

        assert result_peak["predicted_eta_minutes"] >= \
            result_off["predicted_eta_minutes"]

    def test_urgent_reduces_eta(self):
        """Urgent priority should reduce ETA."""
        base = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "kitchen_queue_length": 5,
            "available_runners": 3,
            "is_peak_hour": 0,
        }

        regular = {**base, "priority": "Regular"}
        urgent = {**base, "priority": "Urgent"}

        result_regular = self.predictor.predict(regular)
        result_urgent = self.predictor.predict(urgent)

        assert result_urgent["predicted_eta_minutes"] <= \
            result_regular["predicted_eta_minutes"]

    def test_more_queue_increases_eta(self):
        """Longer kitchen queue should increase ETA."""
        base = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "available_runners": 3,
            "is_peak_hour": 0,
        }

        short_queue = {**base, "kitchen_queue_length": 1}
        long_queue = {**base, "kitchen_queue_length": 15}

        result_short = self.predictor.predict(short_queue)
        result_long = self.predictor.predict(long_queue)

        assert result_long["predicted_eta_minutes"] > \
            result_short["predicted_eta_minutes"]

    def test_fewer_runners_increases_eta(self):
        """Fewer runners should increase ETA."""
        base = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 5,
            "is_peak_hour": 0,
        }

        many_runners = {**base, "available_runners": 5}
        few_runners = {**base, "available_runners": 1}

        result_many = self.predictor.predict(many_runners)
        result_few = self.predictor.predict(few_runners)

        assert result_few["predicted_eta_minutes"] >= \
            result_many["predicted_eta_minutes"]

    def test_never_crashes_with_bad_data(self):
        """Fallback should never crash, even with bad data."""
        bad_data = {}
        result = self.predictor.predict(bad_data)

        # Should return ultimate fallback
        assert result is not None
        assert result["predicted_eta_minutes"] > 0

    def test_never_returns_none(self):
        """Fallback should NEVER return None."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 2,
            "available_runners": 3,
        }
        result = self.predictor.predict(data)
        assert result is not None

    def test_includes_breakdown(self):
        """Result should include time breakdown."""
        data = {
            "items": [{"prep_time": 10, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "kitchen_queue_length": 5,
            "available_runners": 3,
            "is_peak_hour": 0,
        }
        result = self.predictor.predict(data)

        assert "breakdown" in result
        breakdown = result["breakdown"]
        assert "prep_time" in breakdown
        assert "queue_wait" in breakdown
        assert "delivery_time" in breakdown