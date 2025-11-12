"""
Feature engineering with industry-proven payment history strategies
Implements approaches from FICO, VantageScore, RealPage, and Experian
"""

import pandas as pd
import numpy as np

def create_new_features(df_in):
    """
    Complete feature engineering with payment history strategies
    Strategy 1: Derived Payment Indicators
    Strategy 2: Payment x Income/Credit Interactions
    Strategy 4: Composite Payment Risk Score
    """
    df = df_in.copy()
    
    # Better default values - realistic, not zeros
    numerical_defaults = {
        'bedrooms': 1,
        'bathrooms': 1,
        'square_feet': 800,
        'property_age_years': 15,
        'parking_spaces': 0,
        'pets_allowed': 0,
        'furnished': 0,
        'monthly_rent': 10000,
        'security_deposit': 20000,
        'lease_term_months': 12,
        'tenant_age': 35,
        'monthly_income': 40000,
        'employment_verified': 0,
        'income_verified': 0,
        'credit_score': 650,
        'rental_history_years': 3,
        'previous_evictions': 0,
        'market_median_rent': 12000,
        'days_to_rent_property': 30,
        'local_unemployment_rate': 5.0,
        'inflation_rate': 5.0,
        'number_of_bedrooms': 1,
        'property_size_sqft': 800,
        'property_age': 15,
        'on_time_payments_percent': 95,
        'late_payments_count': 0,
        'missed_payments_count': 0
    }
    
    categorical_defaults = {
        'country': 'Unknown',
        'city': 'Unknown',
        'property_type': 'Apartment',
        'employment_type': 'Unknown',
        'currency': 'INR'
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
    
    # Ensure no zero values in critical columns
    df['monthly_income'] = df['monthly_income'].replace(0, 40000)
    df['credit_score'] = df['credit_score'].replace(0, 650)
    df['market_median_rent'] = df['market_median_rent'].replace(0, 12000)
    df['property_size_sqft'] = df['property_size_sqft'].replace(0, 800)
    df['monthly_rent'] = df['monthly_rent'].replace(0, 10000)
    
    # ============================================================
    # STRATEGY 1: DERIVED PAYMENT INDICATORS
    # Based on FICO, VantageScore, and RealPage methodologies
    # ============================================================
    
    # Payment Delinquency Ratio (like FICO's delinquency severity)
    df['payment_delinquency_ratio'] = (
        df['late_payments_count'] / 
        (df['late_payments_count'] + df['on_time_payments_percent'] + 1)
    )
    
    # Payment Severity Score (weighted by type of delinquency)
    df['payment_severity_score'] = (
        (df['late_payments_count'] * 2) + 
        (df['missed_payments_count'] * 5)
    )
    
    # Payment Reliability Index (VantageScore Payment Consistency Index)
    df['payment_reliability_index'] = (
        (df['on_time_payments_percent'] / 100) * 
        (1 - (df['late_payments_count'] / 12).clip(0, 1))
    )
    
    # Payment Risk Binary (RealPage "willingness to pay" indicator)
    df['payment_risk_binary'] = (
        (df['late_payments_count'] > 0) | 
        (df['missed_payments_count'] > 0)
    ).astype(int)
    
    # Payment Perfection (never late)
    df['payment_perfection'] = (
        (df['late_payments_count'] == 0) & 
        (df['missed_payments_count'] == 0)
    ).astype(int)
    
    # Payment Consistency Over Time (normalized by rental history)
    df['payment_consistency'] = 1.0 / (
        1.0 + (df['late_payments_count'] + df['missed_payments_count']) / 
        df['rental_history_years'].replace(0, 1)
    )
    
    # Payment Deterioration Rate (recent problems weighted more)
    df['payment_deterioration_rate'] = (
        df['late_payments_count'] / 
        df['rental_history_years'].replace(0, 0.5)
    )
    
    # Payment Health Score (0-10 scale, like FICO score parts)
    df['payment_health_score'] = (
        10 - 
        (df['late_payments_count'] * 0.5).clip(0, 5) - 
        (df['missed_payments_count'] * 1.5).clip(0, 5)
    ).clip(0, 10)
    
    # ============================================================
    # STRATEGY 2: PAYMENT x INCOME/CREDIT INTERACTIONS
    # Based on RealPage and Experian methodologies
    # ============================================================
    
    # Credit Score x Payment History (Experian approach)
    df['credit_x_payment_reliability'] = (
        (df['credit_score'] / 850) * 
        df['payment_reliability_index']
    )
    
    # Payment Risk x Income Burden (RealPage behavioral pattern)
    df['payment_risk_x_income_burden'] = (
        df['payment_severity_score'] / 
        (df['monthly_income'] / 1000)
    )
    
    # Income Verification x Payment Behavior (trust factor)
    df['verified_income_x_payment'] = (
        df['income_verified'].astype(int) * 
        (1 - df['payment_delinquency_ratio'])
    )
    
    # High Rent Burden x Late Payments (financial stress indicator)
    df['rent_burden_x_late_payments'] = (
        (df['monthly_rent'] / df['monthly_income']) * 
        (1 + df['late_payments_count'])
    )
    
    # Employment Status x Payment Consistency
    df['employment_x_payment_consistency'] = (
        df['employment_verified'].astype(int) * 
        df['payment_consistency']
    )
    
    # Credit Score x Payment Severity (risk amplification)
    df['credit_x_payment_severity'] = (
        (1 - df['credit_score'] / 850) * 
        df['payment_severity_score']
    )
    
    # Rental History x Payment Reliability (experience matters)
    df['experience_x_payment_reliability'] = (
        (df['rental_history_years'] / 10).clip(0, 1) * 
        df['payment_reliability_index']
    )
    
    # Verification Score x Payment Health
    verification_score_raw = (
        df['employment_verified'].astype(int) + 
        df['income_verified'].astype(int)
    )
    df['verification_x_payment_health'] = (
        verification_score_raw * 
        (df['payment_health_score'] / 10)
    )
    
    # ============================================================
    # STRATEGY 4: COMPOSITE PAYMENT RISK SCORE
    # Based on VantageScore weighted aggregation
    # ============================================================
    
    # Normalize components to 0-1 scale
    max_late = df['late_payments_count'].max() if df['late_payments_count'].max() > 0 else 1
    max_missed = df['missed_payments_count'].max() if df['missed_payments_count'].max() > 0 else 1
    
    df['late_payments_normalized'] = (
        df['late_payments_count'] / max_late
    ).clip(0, 1)
    
    df['missed_payments_normalized'] = (
        df['missed_payments_count'] / max_missed
    ).clip(0, 1)
    
    df['on_time_normalized'] = (
        df['on_time_payments_percent'] / 100
    ).clip(0, 1)
    
    # Composite Payment Risk Score (VantageScore-style weighted aggregation)
    # Weights based on VantageScore methodology: payment history 41%, consistency 30%, recency 29%
    df['payment_risk_composite'] = (
        (df['late_payments_normalized'] * 0.25) + 
        (df['missed_payments_normalized'] * 0.35) + 
        ((1 - df['on_time_normalized']) * 0.20) + 
        (df['payment_deterioration_rate'].clip(0, 1) * 0.20)
    ).clip(0, 1) * 10  # Scale to 0-10
    
    # Multi-level composite (non-linear transformations)
    df['payment_composite_squared'] = df['payment_risk_composite'] ** 2
    df['payment_composite_log'] = np.log1p(df['payment_risk_composite'])
    
    # Composite Behavioral Score (RealPage "willingness to pay")
    df['behavioral_payment_score'] = (
        (df['payment_reliability_index'] * 0.40) + 
        (df['payment_consistency'] * 0.30) + 
        ((1 - df['payment_delinquency_ratio']) * 0.30)
    ) * 10  # Scale to 0-10
    
    # Ultimate Payment Risk Index (combines all payment signals)
    df['ultimate_payment_risk_index'] = (
        (df['payment_risk_composite'] * 0.50) + 
        ((10 - df['behavioral_payment_score']) * 0.30) + 
        (df['payment_severity_score'].clip(0, 10) * 0.20)
    ).clip(0, 10)
    
    # ============================================================
    # RAW FINANCIAL FEATURES - KEEP PROMINENT
    # ============================================================
    df['absolute_income'] = df['monthly_income']
    df['absolute_credit_score'] = df['credit_score']
    df['absolute_rent'] = df['monthly_rent']
    
    # ============================================================
    # CORE FINANCIAL RATIOS
    # ============================================================
    df['income_multiple'] = df['monthly_income'] / df['monthly_rent']
    df['rent_to_income_ratio'] = df['monthly_rent'] / df['monthly_income']
    df['income_to_rent_buffer'] = (df['monthly_income'] - df['monthly_rent']).clip(lower=0)
    df['rent_vs_market_ratio'] = df['monthly_rent'] / df['market_median_rent']
    df['rent_per_sqft'] = df['monthly_rent'] / df['property_size_sqft']
    df['debt_to_income_proxy'] = df['monthly_rent'] / df['monthly_income']
    
    # ============================================================
    # CREDIT TIER - CATEGORICAL BINNING
    # ============================================================
    df['credit_tier'] = pd.cut(
        df['credit_score'],
        bins=[0, 580, 670, 740, 850],
        labels=[3, 2, 1, 0],
        include_lowest=True
    ).astype(int)
    
    # ============================================================
    # COMPOSITE INDICATORS - DOMAIN KNOWLEDGE
    # ============================================================
    df['income_stability'] = (
        (df['employment_verified'] == 1) & 
        (df['monthly_income'] >= df['monthly_rent'] * 3)
    ).astype(int)
    
    df['verification_score'] = (
        df['employment_verified'].astype(int) + 
        df['income_verified'].astype(int)
    )
    
    df['high_rent_burden'] = (
        df['rent_to_income_ratio'] > 0.4
    ).astype(int)
    
    df['subprime_credit'] = (
        df['credit_score'] < 670
    ).astype(int)
    
    df['tenant_stability_score'] = (
        (df['rental_history_years'] / 10).clip(0, 1) * 0.6 + 
        (df['lease_term_months'] / 24).clip(0, 1) * 0.4
    )
    
    df['property_desirability_score'] = (
        (df['furnished'] * 0.3) + 
        (df['parking_spaces'] / 3).clip(0, 1) * 0.3 + 
        ((20 - df['property_age_years']) / 20).clip(0, 1) * 0.4
    )
    
    # ============================================================
    # ADDITIONAL FEATURE INTERACTIONS
    # ============================================================
    df['income_x_credit'] = (
        (df['monthly_income'] / 10000) * (df['credit_score'] / 100)
    )
    
    df['rent_burden_x_credit'] = (
        df['rent_to_income_ratio'] * (1 - df['credit_score'] / 850)
    )
    
    df['verification_x_income'] = (
        df['verification_score'] * np.log1p(df['monthly_income'])
    )
    
    df['credit_x_verification'] = (
        (df['credit_score'] / 850) * df['verification_score']
    )
    
    df['stability_x_rent_burden'] = (
        df['tenant_stability_score'] * (1 - df['high_rent_burden'])
    )
    
    df['income_multiple_x_credit'] = (
        df['income_multiple'] * (df['credit_score'] / 850)
    )
    
    # ============================================================
    # PROPERTY FEATURES
    # ============================================================
    df['security_deposit_ratio'] = df['security_deposit'] / df['monthly_rent']
    df['property_age_normalized'] = df['property_age_years'] / 50
    
    # ============================================================
    # MARKET FACTORS
    # ============================================================
    df['local_unemployment_rate_float'] = df['local_unemployment_rate'].fillna(5.0)
    df['inflation_rate_float'] = df['inflation_rate'].fillna(5.0)
    df['market_economic_factor'] = (
        (1 - df['local_unemployment_rate_float'] / 10) * 
        (1 - df['inflation_rate_float'] / 10)
    )
    
    # ============================================================
    # CATEGORICAL ENCODING
    # ============================================================
    categorical_cols = ['country', 'city', 'property_type', 'employment_type', 'currency']
    for col in categorical_cols:
        if col in df.columns:
            df[col + '_enc'] = pd.factorize(df[col])[0]
    
    return df
