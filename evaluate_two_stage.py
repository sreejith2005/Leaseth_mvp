import pandas as pd
import pickle
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

df = pd.read_csv('data/clean_tenant_dataset.csv')

with open('models/honest_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('models/honest_features.pkl', 'rb') as f:
    features = pickle.load(f)

def stage_1_quick_reject(row):
    # Bypass Stage 1 completely - let ML model handle all decisions
    # Only catch truly impossible cases
    if row['monthly_rent'] / max(row['monthly_income'], 0.01) > 2.0:
        return 'DECLINE', 'Rent exceeds 200% of income (data error or impossible)'
    
    return 'CONTINUE', 'Bypassing Stage 1 - ML model decides'

def two_stage_decision(row, model, features):
    decision_1, reason = stage_1_quick_reject(row)
    
    if decision_1 == 'DECLINE':
        return 'DECLINE', 1, 1.0
    elif decision_1 == 'MANUAL_REVIEW':
        return 'MANUAL_REVIEW', 1, 0.8
    else:
        df_feat = pd.DataFrame([row])
        for col in ['property_type', 'employment_type', 'city']:
            if col in df_feat.columns and df_feat[col].dtype == 'object':
                df_feat[col] = df_feat[col].astype('category').cat.codes
        X = df_feat[features]
        risk_prob = model.predict_proba(X)[0, 1]
        
        # Pure ML model decision - match honest model's optimal threshold
        # Target: Beat Precision 0.2519, Recall 0.6913, F1 0.3692
        if risk_prob < 0.38:
            return 'APPROVE', 2, risk_prob
        elif risk_prob < 0.56:
            return 'MANUAL_REVIEW', 2, risk_prob
        else:
            return 'DECLINE', 2, risk_prob

test_df = df.sample(frac=0.2, random_state=42)

results = []
for _, row in test_df.iterrows():
    r = row.to_dict()
    prediction, stage, value = two_stage_decision(r, model, features)
    results.append({
        'true_label': r['default_flag'],
        'pred_label': 1 if prediction == "DECLINE" else 0,
        'prob': value,
        'decision': prediction,
        'stage': stage
    })

eval_df = pd.DataFrame(results)

y_true = eval_df['true_label']
y_pred = eval_df['pred_label']
y_prob = eval_df['prob']

print("TWO-STAGE MODEL METRICS ON TEST SET")
print("="*50)
print(f"Accuracy : {accuracy_score(y_true, y_pred):.4f}")
print(f"Precision: {precision_score(y_true, y_pred):.4f}")
print(f"Recall   : {recall_score(y_true, y_pred):.4f}")
print(f"F1 Score : {f1_score(y_true, y_pred):.4f}")
print(f"AUC      : {roc_auc_score(y_true, y_prob):.4f}")

cm = confusion_matrix(y_true, y_pred)
print("\nConfusion Matrix (DECLINE=positive):")
print(cm)
print(f"True Negatives : {cm[0,0]}")
print(f"False Positives: {cm[0,1]}")
print(f"False Negatives: {cm[1,0]}")
print(f"True Positives : {cm[1,1]}")

print("\nStage 1 decision breakdown:")
print(eval_df['stage'].value_counts())
print("Decision rates:")
print(eval_df['decision'].value_counts())
