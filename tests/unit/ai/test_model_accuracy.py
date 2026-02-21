"""
Model Accuracy Tests
======================
Tests that verify the trained model meets accuracy requirements.
"""

import pytest
import os
import sys
import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..'
))

from ai_module.core.model_loader import ModelLoader
from ai_module.core.feature_engineering import FeatureEngineer


@pytest.mark.ai
class TestModelAccuracy:
    """Tests for trained model accuracy."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Load model and test data."""
        base_dir = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..',
            'ai_module'
        )
        self.model_dir = os.path.join(base_dir, "models")
        self.data_dir = os.path.join(base_dir, "data")

        self.loader = ModelLoader(model_dir=self.model_dir)
        self.model = self.loader.load_model()

        test_path = os.path.join(
            self.data_dir, "test_data.csv"
        )
        if os.path.exists(test_path):
            try:
                self.test_data = pd.read_csv(test_path)
            except EmptyDataError:
                self.test_data = None
        else:
            self.test_data = None

    def test_model_exists(self):
        """Trained model file should exist."""
        if self.model is None:
            pytest.skip(
                "Model not trained yet. "
                "Run: python -m ai_module.scripts.train_model"
            )
        assert self.model is not None

    def test_model_has_predict_method(self):
        """Model should have predict method."""
        if self.model is None:
            pytest.skip("Model not available")
        assert hasattr(self.model, "predict")

    def test_mae_below_threshold(self):
        """Model MAE should be below 3.0 minutes."""
        if self.model is None or self.test_data is None:
            pytest.skip("Model or test data not available")

        features = FeatureEngineer.FEATURE_NAMES
        X_test = self.test_data[features]
        y_test = self.test_data["actual_delivery_minutes"]

        predictions = self.model.predict(X_test)
        mae = np.mean(np.abs(y_test.values - predictions))

        assert mae < 3.0, (
            f"Model MAE ({mae:.4f}) exceeds threshold (3.0)"
        )

    def test_predictions_are_positive(self):
        """All predictions should be positive."""
        if self.model is None or self.test_data is None:
            pytest.skip("Model or test data not available")

        features = FeatureEngineer.FEATURE_NAMES
        X_test = self.test_data[features]
        predictions = self.model.predict(X_test)

        assert all(p > 0 for p in predictions), \
            "Some predictions are non-positive"

    def test_predictions_in_reasonable_range(self):
        """Predictions should be in 1-120 minute range."""
        if self.model is None or self.test_data is None:
            pytest.skip("Model or test data not available")

        features = FeatureEngineer.FEATURE_NAMES
        X_test = self.test_data[features]
        predictions = self.model.predict(X_test)

        assert all(1 <= p <= 120 for p in predictions), \
            "Some predictions are out of reasonable range"

    def test_high_traffic_predicts_higher_eta(self):
        """Higher traffic should predict higher ETA."""
        if self.model is None or self.test_data is None:
            pytest.skip("Model or test data not available")

        features = FeatureEngineer.FEATURE_NAMES
        X_test = self.test_data[features]
        predictions = self.model.predict(X_test)

        low_traffic = predictions[
            self.test_data["active_orders_count"] <= 5
        ]
        high_traffic = predictions[
            self.test_data["active_orders_count"] > 15
        ]

        if len(low_traffic) > 0 and len(high_traffic) > 0:
            assert high_traffic.mean() > low_traffic.mean(), (
                f"High traffic avg ({high_traffic.mean():.1f}) "
                f"should > Low traffic avg ({low_traffic.mean():.1f})"
            )

    def test_more_runners_predicts_lower_eta(self):
        """More runners should predict lower ETA."""
        if self.model is None or self.test_data is None:
            pytest.skip("Model or test data not available")

        features = FeatureEngineer.FEATURE_NAMES
        X_test = self.test_data[features]
        predictions = self.model.predict(X_test)

        few_runners = predictions[
            self.test_data["available_runners"] <= 2
        ]
        many_runners = predictions[
            self.test_data["available_runners"] >= 4
        ]

        if len(few_runners) > 0 and len(many_runners) > 0:
            assert few_runners.mean() > many_runners.mean(), (
                f"Few runners avg ({few_runners.mean():.1f}) "
                f"should > Many runners avg ({many_runners.mean():.1f})"
            )

    def test_model_metadata_exists(self):
        """Model metadata should exist."""
        if self.model is None:
            pytest.skip("Model not available")

        metadata = self.loader.metadata
        if metadata is None:
            pytest.skip("Model metadata not found")

        assert "metrics" in metadata
        assert "mae" in metadata["metrics"]
        assert metadata["metrics"]["mae"] < 3.0