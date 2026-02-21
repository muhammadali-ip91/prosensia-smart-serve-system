"""
Feature Engineering Tests
===========================
Tests for feature extraction and transformation.
"""

import pytest
import numpy as np
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..'
))

from ai_module.core.feature_engineering import FeatureEngineer


@pytest.mark.ai
class TestFeatureEngineer:
    """Tests for the FeatureEngineer class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize feature engineer."""
        self.fe = FeatureEngineer()

    def test_extract_features_shape(self, sample_ai_order_data):
        """Feature vector should have shape (1, 11)."""
        features = self.fe.extract_features(sample_ai_order_data)
        assert features.shape == (1, 11)

    def test_extract_features_type(self, sample_ai_order_data):
        """Features should be numpy array."""
        features = self.fe.extract_features(sample_ai_order_data)
        assert isinstance(features, np.ndarray)

    def test_feature_names_count(self):
        """Should have exactly 11 feature names."""
        assert len(FeatureEngineer.FEATURE_NAMES) == 11

    def test_hour_extraction(self):
        """Hour should be extracted correctly."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
            "order_time": datetime(2024, 1, 15, 14, 30, 0),
        }
        features = self.fe.extract_features(data)
        assert features[0][0] == 14  # hour_of_day

    def test_day_extraction(self):
        """Day of week should be extracted correctly."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
            "order_time": datetime(2024, 1, 15, 10, 0, 0),
            # Jan 15, 2024 is Monday = 0
        }
        features = self.fe.extract_features(data)
        assert features[0][1] == 0  # Monday

    def test_peak_hour_detection(self):
        """Peak hours should be detected correctly."""
        # Peak hour (1 PM)
        peak_data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "Regular",
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
            "order_time": datetime(2024, 1, 15, 13, 0, 0),
        }
        features = self.fe.extract_features(peak_data)
        assert features[0][9] == 1  # is_peak_hour

        # Off-peak hour (10 AM)
        offpeak_data = peak_data.copy()
        offpeak_data["order_time"] = datetime(
            2024, 1, 15, 10, 0, 0
        )
        features = self.fe.extract_features(offpeak_data)
        assert features[0][9] == 0

    def test_priority_encoding(self):
        """Priority should be encoded correctly."""
        base = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
        }

        regular = {**base, "priority": "Regular"}
        urgent = {**base, "priority": "Urgent"}

        feat_regular = self.fe.extract_features(regular)
        feat_urgent = self.fe.extract_features(urgent)

        assert feat_regular[0][10] == 0  # Regular = 0
        assert feat_urgent[0][10] == 1   # Urgent = 1

    def test_item_complexity_calculation(self):
        """Complexity should increase with complex items."""
        simple = {
            "items": [
                {"prep_time": 3, "complexity_score": 1, "quantity": 1}
            ],
            "station_distance": 100, "priority": "Regular",
            "active_orders_count": 5, "available_runners": 3,
            "kitchen_queue_length": 2,
        }
        complex_order = {
            "items": [
                {"prep_time": 20, "complexity_score": 3, "quantity": 3}
            ],
            "station_distance": 100, "priority": "Regular",
            "active_orders_count": 5, "available_runners": 3,
            "kitchen_queue_length": 2,
        }

        feat_simple = self.fe.extract_features(simple)
        feat_complex = self.fe.extract_features(complex_order)

        # item_complexity is index 3
        assert feat_complex[0][3] > feat_simple[0][3]

    def test_missing_required_field_raises_error(self):
        """Missing required field should raise ValueError."""
        incomplete_data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            # Missing station_distance, priority, etc.
        }
        with pytest.raises(ValueError):
            self.fe.extract_features(incomplete_data)

    def test_empty_items_raises_error(self):
        """Empty items list should raise ValueError."""
        data = {
            "items": [],
            "station_distance": 100,
            "priority": "Regular",
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
        }
        with pytest.raises(ValueError):
            self.fe.extract_features(data)

    def test_invalid_priority_raises_error(self):
        """Invalid priority should raise ValueError."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": 100,
            "priority": "SUPER_URGENT",  # Invalid
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
        }
        with pytest.raises(ValueError):
            self.fe.extract_features(data)

    def test_negative_distance_raises_error(self):
        """Negative distance should raise ValueError."""
        data = {
            "items": [{"prep_time": 5, "quantity": 1}],
            "station_distance": -100,  # Invalid
            "priority": "Regular",
            "active_orders_count": 5,
            "available_runners": 3,
            "kitchen_queue_length": 2,
        }
        with pytest.raises(ValueError):
            self.fe.extract_features(data)

    def test_batch_extract(self):
        """Batch extraction should handle multiple orders."""
        orders = [
            {
                "items": [{"prep_time": 5, "quantity": 1}],
                "station_distance": 100,
                "priority": "Regular",
                "active_orders_count": 5,
                "available_runners": 3,
                "kitchen_queue_length": 2,
            },
            {
                "items": [{"prep_time": 15, "quantity": 2}],
                "station_distance": 200,
                "priority": "Urgent",
                "active_orders_count": 10,
                "available_runners": 1,
                "kitchen_queue_length": 8,
            },
        ]
        features = self.fe.batch_extract_features(orders)
        assert features.shape == (2, 11)

    def test_feature_summary(self, sample_ai_order_data):
        """Feature summary should include descriptions."""
        summary = self.fe.get_feature_summary(
            sample_ai_order_data
        )
        assert "kitchen_load" in summary
        assert "runner_availability" in summary
        assert "is_peak_description" in summary
        assert "priority_description" in summary