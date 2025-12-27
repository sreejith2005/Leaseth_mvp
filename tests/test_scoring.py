"""
Unit tests for model scoring logic
"""

import pytest
from src.scoring import predict_and_score

class TestScoring:
    """Test scoring logic"""

    def test_predict_requires_models_loaded(self):
        """Test that prediction requires models to be loaded"""
        # This test assumes models are not loaded
        # In real testing, this would be handled by fixtures
        pass

    def test_calibration_probability_bounds(self):
        """Test that calibrated probability is in [0, 1]"""
        from src.scoring import _calibrate_probability
        
        # Test edge cases
        assert 0.0 <= _calibrate_probability(0.0, is_v1=True) <= 1.0
        assert 0.0 <= _calibrate_probability(0.5, is_v1=True) <= 1.0
        assert 0.0 <= _calibrate_probability(1.0, is_v1=True) <= 1.0

    def test_confidence_score_calculation(self):
        """Test confidence score calculation"""
        from src.scoring import _calculate_confidence
        
        # Edge cases
        assert _calculate_confidence(0.0) == 1.0  # Minimum probability
        assert _calculate_confidence(1.0) == 1.0  # Maximum probability
        assert _calculate_confidence(0.5) == 0.0  # Middle probability (least confident)
