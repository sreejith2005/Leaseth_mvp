"""
Unit tests for feature engineering
"""

import pytest
import pandas as pd
from src.features import create_new_features

class TestFeatureEngineering:
    """Test feature engineering pipeline"""

    def test_create_new_features_basic(self):
        """Test basic feature creation"""
        data = {
            'monthly_income': 50000,
            'monthly_rent': 15000,
            'credit_score': 720,
            'employment_verified': 1,
            'income_verified': 1,
            'rental_history_years': 5,
            'lease_term_months': 12,
            'property_size_sqft': 1000,
            'property_age_years': 5,
            'market_median_rent': 18000,
            'bedrooms': 2,
            'bathrooms': 1,
            'furnished': 0,
            'parking_spaces': 1,
            'pets_allowed': 1,
            'previous_evictions': 0,
            'local_unemployment_rate': 5.0,
            'inflation_rate': 5.0
        }
        
        df = pd.DataFrame([data])
        result = create_new_features(df)
        
        # Assert output is DataFrame
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_composite_features_created(self):
        """Test that composite features are created"""
        data = {
            'monthly_income': 50000,
            'monthly_rent': 15000,
            'credit_score': 720,
            'employment_verified': 1,
            'income_verified': 1,
            'rental_history_years': 5,
            'lease_term_months': 12,
            'property_size_sqft': 1000,
            'market_median_rent': 18000,
            'bedrooms': 2,
            'bathrooms': 1,
            'furnished': 0,
            'parking_spaces': 1,
            'pets_allowed': 1,
            'property_age_years': 5,
            'previous_evictions': 0,
            'local_unemployment_rate': 5.0,
            'inflation_rate': 5.0
        }
        
        df = pd.DataFrame([data])
        result = create_new_features(df)
        
        # Check composite features exist
        assert 'rent_to_income_ratio' in result.columns
        assert 'income_stability' in result.columns
        assert 'verification_score' in result.columns

    def test_missing_values_handled(self):
        """Test handling of missing values"""
        data = {
            'monthly_income': 50000,
            'monthly_rent': 15000
        }
        
        df = pd.DataFrame([data])
        result = create_new_features(df)
        
        # Should not have NaN values in important columns
        assert result['monthly_income'].notna().all()
        assert result['monthly_rent'].notna().all()
