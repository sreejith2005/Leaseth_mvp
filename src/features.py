# src/features.py - Copy from earlier (composite indicators version)
# [Use the code from the earlier chat - WORKING VERSION WITH COMPOSITES]

import pandas as pd
import numpy as np

def create_new_features(df_in):
    """
    Complete feature engineering with all composite indicators.
    This version is proven to work.
    """
    df = df_in.copy()
    
    # Missing data handling
    numerical_defaults = {
        'bedrooms': 1, 'bathrooms': 1, 'square_feet': 500, 'property_age_years': 10,
        'parking_spaces': 0, 'pets_allowed': 0, 'furnished': 0, 'monthly_rent': 0,
        'security_deposit': 0, 'lease_term_months': 12, 'tenant_age': 30,
        'monthly_income': 0, 'employment_verified': 0, 'income_verified': 0,
        'credit_score': 0, 'rental_history_years': 0, 'previous_evictions': 0,
        'market_median_rent': 0, 'days_to_rent_property': 30,
        'local_unemployment_rate': 5.0, 'inflation_rate': 5.0,
        'number_of_bedrooms': 1, 'property_size_sqft': 500, 'property_age': 10
    }
    
    categorical_defaults = {
        'country': 'Unknown', 'city': 'Unknown', 'property_type': 'Apartment',
        'employment_type': 'Unknown', 'currency': 'INR'
    }
    
    for col, default_val in numerical_defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            df[col] = df[col].fillna(default_val)
    
    for col, default_val in categorical_defaults.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            df[col] = df[col].fillna(default_val)
    
    if 'square_feet' in df.columns and 'property_size_sqft' not in df.columns:
        df['property_size_sqft'] = df['square_feet']
    if 'property_age_years' in df.columns and 'property_age' not in df.columns:
        df['property_age'] = df['property_age_years']
    if 'bedrooms' in df.columns and 'number_of_bedrooms' not in df.columns:
        df['number_of_bedrooms'] = df['bedrooms']
    
    # Zero-value safety
    df['monthly_income'] = df['monthly_income'].replace(0, 1)
    df['credit_score'] = df['credit_score'].replace(0, 1)
    df['market_median_rent'] = df['market_median_rent'].replace(0, 1)
    df['property_size_sqft'] = df['property_size_sqft'].replace(0, 1)
    
    # Core financial ratios
    df['rent_to_income_ratio'] = df['monthly_rent'] / df['monthly_income']
    df['income_to_rent_buffer'] = (df['monthly_income'] - df['monthly_rent']).clip(lower=0)
    df['rent_vs_market_ratio'] = df['monthly_rent'] / df['market_median_rent']
    
    # Composite indicators
    df['income_stability'] = ((df['employment_verified'] == 1) & (df['monthly_income'] >= df['monthly_rent'] * 3)).astype(int)
    df['verification_score'] = df['employment_verified'].astype(int) + df['income_verified'].astype(int)
    df['high_rent_burden'] = (df['rent_to_income_ratio'] > 0.4).astype(int)
    df['subprime_credit'] = (df['credit_score'] < 670).astype(int)
    df['tenant_stability_score'] = ((df['rental_history_years'] / 10).clip(0, 1) * 0.6 + (df['lease_term_months'] / 24).clip(0, 1) * 0.4)
    df['property_desirability_score'] = ((df['furnished'] * 0.3) + (df['parking_spaces'] / 3).clip(0, 1) * 0.3 + ((20 - df['property_age_years']) / 20).clip(0, 1) * 0.4)
    df['rent_per_sqft'] = df['monthly_rent'] / df['property_size_sqft']
    df['credit_income_interaction'] = (df['credit_score'] / 850) * (df['monthly_income'] / 100000)
    df['rent_credit_ratio'] = df['monthly_rent'] / df['credit_score']
    
    # Categorical encoding
    categorical_cols = ['country', 'city', 'property_type', 'employment_type', 'currency']
    for col in categorical_cols:
        if col in df.columns:
            df[col + '_enc'] = pd.factorize(df[col])[0]
    
    return df
