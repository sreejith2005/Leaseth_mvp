"""
Feature Engineering Module for Leaseth

This module handles feature engineering and transformation for the ML models.
Computes composite indicators like rent_to_income_ratio, income_stability, etc.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def create_new_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create engineered features for the ML model.
    
    Args:
        df: Input DataFrame with raw applicant data
        
    Returns:
        DataFrame with additional computed features
    """
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Composite financial indicators
    df['rent_to_income_ratio'] = df['monthly_rent'] / df['monthly_income'].replace(0, 1)
    
    df['income_stability'] = (
        (df['employment_verified'] == 1) & 
        (df['monthly_income'] >= df['monthly_rent'] * 3)
    ).astype(int)
    
    df['verification_score'] = (
        df['employment_verified'].astype(int) + 
        df['income_verified'].astype(int)
    )
    
    df['high_rent_burden'] = (df['rent_to_income_ratio'] > 0.4).astype(int)
    df['subprime_credit'] = (df['credit_score'] < 670).astype(int)
    
    # Tenant stability score
    df['tenant_stability_score'] = (
        (df['rental_history_years'] / 10).clip(0, 1) * 0.6 + 
        (df['lease_term_months'] / 24).clip(0, 1) * 0.4
    )
    
    # Payment reliability
    df['payment_reliability'] = (
        df['on_time_payments_percent'] / 100 * 0.7 +
        (1 - df['late_payments_count'] / 12).clip(0, 1) * 0.3
    )
    
    return df


def extract_features_from_dict(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert a dictionary of applicant data to a DataFrame with features.
    
    Args:
        data: Dictionary with applicant information
        
    Returns:
        DataFrame with one row containing all features
    """
    df = pd.DataFrame([data])
    df = create_new_features(df)
    return df
