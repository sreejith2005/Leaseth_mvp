"""
Feature engineering with composite scoring for balanced model (V2)
Includes: V1 (all features), V2 (behavioral with composites), V3 (financial only)
"""

import pandas as pd
import numpy as np

def create_new_features(df_in):
    """
    Complete feature engineering with multiple strategies
    Returns dataframe with ALL features (V1, V2, V3 selection happens in training)
    """
    df = df_in.copy()
    
    # Better default values - realistic, not zeros
    numerical_defaults = {
        'bedrooms': 1, 'bathrooms': 1, 'square_feet': 800, 'property_age_years': 15,
        'parking_spaces': 0, 'pets_allowed': 0, 'furnished': 0, 'monthly_rent': 10000,
        'security_deposit': 20000, 'lease_term_months': 12, 'tenant_age': 35,
        'monthly_income': 40000, 'employment_verified': 0, 'income_verified': 0,
        'credit_score': 650, 'rental_history_years': 3, 'previous_evictions': 0,
        'on_time_payments': 0, 'late_payments': 0, 'missed_payments': 0,
        'market_median_rent': 12000, 'days_to_rent_property': 30,
        'local_unemployment_rate': 5.0, 'inflation_rate': 5.0
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
    
    # Ensure no zero values in critical columns
    df['monthly_income'] = df['monthly_income'].replace(0, 40000)
    df['credit_score'] = df['credit_score'].replace(0, 650)
    df['market_median_rent'] = df['market_median_rent'].replace(0, 12000)
    df['square_feet'] = df['square_feet'].replace(0, 800)
    df['monthly_rent'] = df['monthly_rent'].replace(0, 10000)
    
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
    df['rent_per_sqft'] = df['monthly_rent'] / df['square_feet']
    df['debt_to_income_proxy'] = df['monthly_rent'] / df['monthly_income']
    df['security_deposit_ratio'] = df['security_deposit'] / df['monthly_rent']
    
    # ============================================================
    # PAYMENT HISTORY FEATURES
    # ============================================================
    df['payment_delinquency_ratio'] = (
        df['late_payments'] / (df['late_payments'] + df['on_time_payments'] + 1)
    )
    
    df['payment_severity_score'] = (
        (df['late_payments'] * 2) + (df['missed_payments'] * 5)
    )
    
    df['payment_reliability_index'] = (
        (df['on_time_payments'] / (df['on_time_payments'] + df['late_payments'] + df['missed_payments'] + 1)) *
        (1 - (df['late_payments'] / 12).clip(0, 1))
    )
    
    df['payment_risk_binary'] = (
        (df['late_payments'] > 0) | (df['missed_payments'] > 0)
    ).astype(int)
    
    df['payment_perfection'] = (
        (df['late_payments'] == 0) & (df['missed_payments'] == 0)
    ).astype(int)
    
    df['payment_consistency'] = 1.0 / (
        1.0 + (df['late_payments'] + df['missed_payments']) / df['rental_history_years'].replace(0, 1)
    )
    
    df['payment_deterioration_rate'] = (
        df['late_payments'] / df['rental_history_years'].replace(0, 0.5)
    )
    
    df['payment_health_score'] = (
        10 - (df['late_payments'] * 0.5).clip(0, 5) - (df['missed_payments'] * 1.5).clip(0, 5)
    ).clip(0, 10)
    
    # ============================================================
    # CORE COMPOSITE SCORES FOR V2 (Behavioral Model)
    # ============================================================
    
    # 1. PAYMENT BEHAVIOR COMPOSITE
    df['payment_behavior_composite'] = (
        (df['on_time_payments'] * 0.5) - 
        (df['late_payments'] * 0.3) - 
        (df['missed_payments'] * 0.8) + 
        (df['payment_consistency'] * 0.2)
    ).clip(0, 10)
    
    # 2. FINANCIAL RESPONSIBILITY SCORE
    df['financial_responsibility_score'] = (
        (df['credit_score'] / 850 * 0.3) +
        ((1 - df['rent_to_income_ratio'].clip(0, 1)) * 0.4) +
        ((df['monthly_income'] > df['monthly_rent'] * 2).astype(int) * 0.2) +
        (df['income_verified'].astype(int) * 0.1)
    ) * 10  # Scale to 0-10
    
    # 3. TENANT HISTORY SCORE
    df['tenant_history_score'] = (
        (df['rental_history_years'] / 20).clip(0, 1) * 0.4 +
        ((12 - df['previous_evictions'].clip(0, 12)) / 12 * 0.6)
    ) * 10
    
    # 4. PROPERTY/MARKET RISK SCORE
    df['property_market_risk'] = (
        (df['monthly_rent'] / df['market_median_rent'] * 0.3) +
        ((20 - df['property_age_years'].clip(0, 20)) / 20 * 0.2) +
        ((1 - df['local_unemployment_rate'] / 20).clip(0, 1) * 0.3) +
        ((1 - df['inflation_rate'] / 10).clip(0, 1) * 0.2)
    ) * 10
    
    # 5. EMPLOYMENT CREDIBILITY (COMPOSITE)
    df['employment_credibility'] = (
        df['employment_verified'].astype(int) * 0.6 +
        (df['income_verified'].astype(int) * 0.4)
    ) * 10
    
    # ============================================================
    # PAYMENT × INCOME/CREDIT INTERACTIONS
    # ============================================================
    df['credit_x_payment_reliability'] = (
        (df['credit_score'] / 850) * df['payment_reliability_index']
    )
    
    df['payment_risk_x_income_burden'] = (
        df['payment_severity_score'] / (df['monthly_income'] / 1000)
    )
    
    df['verified_income_x_payment'] = (
        df['income_verified'].astype(int) * (1 - df['payment_delinquency_ratio'])
    )
    
    df['rent_burden_x_late_payments'] = (
        (df['monthly_rent'] / df['monthly_income']) * (1 + df['late_payments'])
    )
    
    df['employment_x_payment_consistency'] = (
        df['employment_verified'].astype(int) * df['payment_consistency']
    )
    
    df['credit_x_payment_severity'] = (
        (1 - df['credit_score'] / 850) * df['payment_severity_score']
    )
    
    df['experience_x_payment_reliability'] = (
        (df['rental_history_years'] / 10).clip(0, 1) * df['payment_reliability_index']
    )
    
    verification_score_raw = (
        df['employment_verified'].astype(int) + df['income_verified'].astype(int)
    )
    df['verification_x_payment_health'] = (
        verification_score_raw * (df['payment_health_score'] / 10)
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
        verification_score_raw * np.log1p(df['monthly_income'])
    )
    
    df['credit_x_verification'] = (
        (df['credit_score'] / 850) * verification_score_raw
    )
    
    df['stability_x_rent_burden'] = (
        df['payment_consistency'] * (1 - (df['rent_to_income_ratio'] > 0.4).astype(int))
    )
    
    df['income_multiple_x_credit'] = (
        df['income_multiple'] * (df['credit_score'] / 850)
    )
    
    # ============================================================
    # COMPOSITE RISK SCORES
    # ============================================================
    max_late = df['late_payments'].max() if df['late_payments'].max() > 0 else 1
    max_missed = df['missed_payments'].max() if df['missed_payments'].max() > 0 else 1
    
    df['late_payments_normalized'] = (df['late_payments'] / max_late).clip(0, 1)
    df['missed_payments_normalized'] = (df['missed_payments'] / max_missed).clip(0, 1)
    df['on_time_normalized'] = (df['on_time_payments'] / (df['on_time_payments'].max() + 1)).clip(0, 1)
    
    df['payment_risk_composite'] = (
        (df['late_payments_normalized'] * 0.25) +
        (df['missed_payments_normalized'] * 0.35) +
        ((1 - df['on_time_normalized']) * 0.20) +
        (df['payment_deterioration_rate'].clip(0, 1) * 0.20)
    ).clip(0, 1) * 10
    
    df['payment_composite_squared'] = df['payment_risk_composite'] ** 2
    df['payment_composite_log'] = np.log1p(df['payment_risk_composite'])
    
    df['behavioral_payment_score'] = (
        (df['payment_reliability_index'] * 0.40) +
        (df['payment_consistency'] * 0.30) +
        ((1 - df['payment_delinquency_ratio']) * 0.30)
    ) * 10
    
    df['ultimate_payment_risk_index'] = (
        (df['payment_risk_composite'] * 0.50) +
        ((10 - df['behavioral_payment_score']) * 0.30) +
        (df['payment_severity_score'].clip(0, 10) * 0.20)
    ).clip(0, 10)
    
    # ============================================================
    # CATEGORICAL ENCODING
    # ============================================================
    df['property_age_normalized'] = df['property_age_years'] / 50
    df['local_unemployment_rate_float'] = df['local_unemployment_rate'].fillna(5.0)
    df['inflation_rate_float'] = df['inflation_rate'].fillna(5.0)
    
    df['market_economic_factor'] = (
        (1 - df['local_unemployment_rate_float'] / 10) *
        (1 - df['inflation_rate_float'] / 10)
    )
    
    # Credit tier
    df['credit_tier'] = pd.cut(
        df['credit_score'],
        bins=[0, 580, 670, 740, 850],
        labels=[3, 2, 1, 0],
        include_lowest=True
    ).astype(int)
    
    # Composite indicators
    df['income_stability'] = (
        (df['employment_verified'] == 1) & (df['monthly_income'] >= df['monthly_rent'] * 3)
    ).astype(int)
    
    df['verification_score'] = (
        df['employment_verified'].astype(int) + df['income_verified'].astype(int)
    )
    
    df['high_rent_burden'] = (df['rent_to_income_ratio'] > 0.4).astype(int)
    df['subprime_credit'] = (df['credit_score'] < 670).astype(int)
    
    df['tenant_stability_score'] = (
        (df['rental_history_years'] / 10).clip(0, 1) * 0.6 +
        (df['lease_term_months'] / 24).clip(0, 1) * 0.4
    )
    
    df['property_desirability_score'] = (
        (df['furnished'] * 0.3) +
        ((df['parking_spaces'] / 3).clip(0, 1) * 0.3) +
        (((20 - df['property_age_years']) / 20).clip(0, 1) * 0.4)
    )
    
    # Categorical encoding
    categorical_cols = ['country', 'city', 'property_type', 'employment_type', 'currency']
    for col in categorical_cols:
        if col in df.columns:
            df[col + '_enc'] = pd.factorize(df[col])[0]
    
    return df
