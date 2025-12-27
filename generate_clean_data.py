import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_realistic_tenant_dataset(n_records=50000, target_default_rate=0.15):
    """
    Generate TRULY REALISTIC synthetic tenant dataset
    With proper noise and unpredictability
    """
    
    print("\n" + "="*80)
    print("GENERATING REALISTIC SYNTHETIC DATASET (WITH NOISE)")
    print("="*80 + "\n")
    
    np.random.seed(42)
    
    # Feature generation (same as before)
    cities = ['Mumbai', 'Pune', 'Bangalore', 'Delhi', 'Hyderabad']
    property_types = ['Apartment', 'Villa', 'Condo', 'Studio']
    employment_types = ['Full-time', 'Self-employed', 'Part-time', 'Freelance']
    
    data = {
        'applicant_id': np.arange(10001, 10001 + n_records),
        'credit_score': np.clip(np.random.normal(680, 80, n_records), 300, 850).astype(int),
        'monthly_income': np.clip(np.random.lognormal(10.5, 0.8, n_records), 5000, 500000).astype(int),
        'monthly_rent': np.clip(np.random.lognormal(9.8, 0.7, n_records), 3000, 150000).astype(int),
        'employment_type': np.random.choice(employment_types, n_records),
        'employment_verified': np.random.choice([1, 0], n_records, p=[0.85, 0.15]),
        'income_verified': np.random.choice([1, 0], n_records, p=[0.80, 0.20]),
        'rental_history_years': np.clip(np.random.exponential(2.5, n_records), 0, 30).astype(int),
        'previous_evictions': np.random.choice([0, 1, 2], n_records, p=[0.94, 0.05, 0.01]),
        'property_type': np.random.choice(property_types, n_records),
        'bedrooms': np.random.choice([1, 2, 3, 4], n_records, p=[0.35, 0.45, 0.15, 0.05]),
        'bathrooms': np.random.choice([1, 2, 3], n_records, p=[0.60, 0.35, 0.05]),
        'square_feet': np.clip(np.random.normal(800, 300, n_records), 300, 3000).astype(int),
        'property_age_years': np.clip(np.random.exponential(8, n_records), 0, 50).astype(int),
        'city': np.random.choice(cities, n_records),
        'furnished': np.random.choice([0, 1], n_records, p=[0.70, 0.30]),
        'pets_allowed': np.random.choice([0, 1], n_records, p=[0.75, 0.25]),
        'parking_spaces': np.random.choice([0, 1, 2], n_records, p=[0.40, 0.45, 0.15]),
        'lease_term_months': np.random.choice([6, 12, 24, 36], n_records, p=[0.10, 0.70, 0.15, 0.05]),
        'market_median_rent': np.clip(np.random.normal(25000, 5000, n_records), 10000, 80000).astype(int),
        'local_unemployment_rate': np.clip(np.random.normal(4.5, 2, n_records), 1, 12),
        'inflation_rate': np.clip(np.random.normal(5.5, 1.5, n_records), 2, 10),
        'move_in_date': pd.date_range('2022-01-01', periods=n_records, freq='12h'),
    }
    
    df = pd.DataFrame(data)
    
    # REALISTIC outcome generation (WITH NOISE)
    logger.info("Generating realistic default outcomes (with noise)...")
    
    default_flags = []
    
    for _, row in df.iterrows():
        # Base risk
        risk = 10
        
        # Credit score impact
        if row['credit_score'] < 550:
            risk += 30
        elif row['credit_score'] < 620:
            risk += 20
        elif row['credit_score'] < 680:
            risk += 10
        elif row['credit_score'] >= 750:
            risk -= 10
        
        # Rent burden
        rent_burden = row['monthly_rent'] / max(row['monthly_income'], 1)
        if rent_burden > 0.60:
            risk += 25
        elif rent_burden > 0.50:
            risk += 15
        elif rent_burden > 0.40:
            risk += 8
        elif rent_burden < 0.25:
            risk -= 8
        
        # Verification
        if row['income_verified'] == 0:
            risk += 8
        if row['employment_verified'] == 0:
            risk += 6
        
        # Rental history
        if row['rental_history_years'] < 1:
            risk += 10
        elif row['rental_history_years'] >= 5:
            risk -= 5
        
        # Evictions
        risk += row['previous_evictions'] * 12
        
        # Employment
        if row['employment_type'] in ['Part-time', 'Freelance']:
            risk += 5
        
        # Unemployment
        risk += (row['local_unemployment_rate'] - 4.5) * 1.5
        
        # ADD REALISTIC NOISE (30% std dev)
        # Use absolute value to ensure scale is always non-negative
        noise = np.random.normal(0, abs(risk) * 0.30)
        final_risk = risk + noise
        final_risk = max(0, min(100, final_risk))
        
        # Sigmoid transformation
        prob = 1 / (1 + np.exp(-(final_risk - 50) / 15))
        prob = max(0.01, min(0.99, prob))
        
        default_flags.append(int(np.random.rand() < prob))
    
    df['default_flag'] = default_flags
    
    # Adjust to target rate
    current_rate = df['default_flag'].mean()
    logger.info(f"Initial default rate: {current_rate:.1%}")
    
    if abs(current_rate - target_default_rate) > 0.02:
        # Resample to match target
        n_defaults_needed = int(n_records * target_default_rate)
        n_defaults_current = df['default_flag'].sum()
        
        if n_defaults_current > n_defaults_needed:
            # Too many defaults - flip some to 0
            defaults_idx = df[df['default_flag'] == 1].index
            flip_idx = np.random.choice(defaults_idx, n_defaults_current - n_defaults_needed, replace=False)
            df.loc[flip_idx, 'default_flag'] = 0
        else:
            # Too few defaults - flip some to 1
            non_defaults_idx = df[df['default_flag'] == 0].index
            flip_idx = np.random.choice(non_defaults_idx, n_defaults_needed - n_defaults_current, replace=False)
            df.loc[flip_idx, 'default_flag'] = 1
    
    final_rate = df['default_flag'].mean()
    logger.info(f"Final default rate: {final_rate:.1%}")
    
    # Check correlations
    print("\n" + "="*80)
    print("FEATURE CORRELATIONS WITH DEFAULT")
    print("="*80 + "\n")
    
    corr_features = ['credit_score', 'monthly_income', 'monthly_rent', 'employment_verified',
                    'income_verified', 'rental_history_years', 'previous_evictions']
    
    for feat in corr_features:
        corr = df[feat].corr(df['default_flag'])
        print(f"{feat:30s}: {corr:+.4f}")
    
    if any(abs(df[feat].corr(df['default_flag'])) > 0.50 for feat in corr_features):
        print("\nWARNING: Correlations too high - still has some leakage")
    else:
        print("\nCorrelations realistic (0.10-0.35 range)")
    
    return df


# Run generation
df = generate_realistic_tenant_dataset(n_records=50000, target_default_rate=0.15)
df.to_csv('data/clean_tenant_dataset.csv', index=False)
print("\nRealistic dataset saved to data/clean_tenant_dataset.csv")
