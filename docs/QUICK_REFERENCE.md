# Quick Reference: Three-Tier System

## Decision Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                     THREE-TIER DECISION SYSTEM                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  TIER 1: AUTO_APPROVE    (probability < 35%)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ✓ Fast-track approval                                     │   │
│  │ ✓ Minimal friction for applicants                         │   │
│  │ ✓ Expected default rate: <5%                              │   │
│  │ ✓ Example: Credit 780, Income 8k, Rent 2k, 0 evictions   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  TIER 2: MANUAL_REVIEW   (35% ≤ probability < 85%)              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ⚠ Requires human review                                   │   │
│  │ ⚠ Check references, employment, bank statements           │   │
│  │ ⚠ Consider: co-signer, increased deposit, shorter lease   │   │
│  │ ⚠ Sub-tiers: LOW-MEDIUM → MEDIUM → MEDIUM-HIGH           │   │
│  │ ⚠ Prioritize review by sub-tier and probability           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  TIER 3: AUTO_REJECT     (probability ≥ 85%)                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ✗ Automatic rejection                                      │   │
│  │ ✗ Only extreme cases: 2+ evictions + credit <600          │   │
│  │ ✗ Even then, may downgrade to manual review               │   │
│  │ ✗ Expected: 5-15% of applicants                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Cost Context

```
Business Reality: FP Cost > FN Cost
────────────────────────────────────────────────────────────
False Positive (rejecting good tenant):  $5,000 (vacancy)
False Negative (accepting bad tenant):   $3,000 (eviction)
Cost Ratio:                               1.67x

Implication: Be conservative with rejections
```

## Threshold Adjustment Cheat Sheet

| Situation | Auto-Approve | Action |
|-----------|--------------|--------|
| **High vacancy** (>10%) | **INCREASE** (+0.05) | Need tenants |
| **Low vacancy** (<3%) | **DECREASE** (-0.05) | Be selective |
| **Many applicants** | **DECREASE** (-0.03) | Can choose |
| **Few applicants** | **INCREASE** (+0.03) | Be lenient |
| **FP cost >> FN cost** | **INCREASE** (+0.05) | Avoid rejecting good |
| **FN cost >> FP cost** | **DECREASE** (-0.05) | Avoid accepting bad |

## API Integration

### Request with Custom Thresholds
```json
POST /api/v1/score
{
  "applicant_id": "APP123",
  "name": "John Doe",
  "monthly_income": 5000,
  "credit_score": 720,
  "monthly_rent": 1500,
  "custom_thresholds": {
    "auto_approve": 0.30,
    "manual_review": 0.70,
    "auto_reject": 0.85
  }
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "risk_score": 42,
    "risk_category": "MEDIUM",
    "recommendation": "MANUAL_REVIEW",
    "decision_tier": "TIER_2_MANUAL_REVIEW",
    "decision_reasoning": "Elevated risk (42%). Consider co-signer or increased deposit.",
    "confidence_score": 0.84,
    "model_version": "V3_2025_11"
  }
}
```

## Python Usage

### Calculate Dynamic Thresholds
```python
from src.scoring import calculate_dynamic_thresholds

# High vacancy season
thresholds = calculate_dynamic_thresholds(
    fp_cost=5000,
    fn_cost=3000,
    vacancy_rate=0.12,
    application_volume="low"
)
# Returns: {"auto_approve": 0.40, "manual_review": 0.75, "auto_reject": 0.90}

# Hot market
thresholds = calculate_dynamic_thresholds(
    fp_cost=5000,
    fn_cost=3000,
    vacancy_rate=0.02,
    application_volume="high"
)
# Returns: {"auto_approve": 0.32, "manual_review": 0.67, "auto_reject": 0.85}
```

### Manual Review Guidance by Sub-Tier

**LOW-MEDIUM (35-50%)**
- ✅ Likely approve with basic verification
- Check: Employment letter, 1 month pay stub
- Tip: Good candidates, minor concerns

**MEDIUM (50-70%)**
- ⚠ Approve with conditions
- Check: 3 months bank statements, references
- Tip: Consider increased deposit (1.5x) or co-signer

**MEDIUM-HIGH (70-85%)**
- ⚠ High scrutiny required
- Check: Full financial history, rental references, background
- Tip: Shorter lease term (6 months) or guarantor required

## Key Metrics to Monitor

### Daily/Weekly
- Distribution: AUTO_APPROVE / MANUAL_REVIEW / AUTO_REJECT
- Expected: 40-50% / 35-45% / 5-15%

### Monthly
- Actual default rate per tier
  - AUTO_APPROVE should be <5%
  - MANUAL_REVIEW should be 10-20%
  - AUTO_REJECT (if approved) should be >70%

### Quarterly
- Total cost: FP cost + FN cost
- Compare to baseline
- Adjust thresholds if costs increase

## Common Scenarios

### Scenario 1: Too Many Manual Reviews
**Symptom:** 60%+ go to manual review
**Solution:** Lower auto_approve threshold (e.g., 0.35 → 0.40)
**Effect:** More AUTO_APPROVE, fewer reviews

### Scenario 2: High Auto-Approve Default Rate
**Symptom:** AUTO_APPROVE tier has >10% defaults
**Solution:** Raise auto_approve threshold (e.g., 0.35 → 0.30)
**Effect:** Fewer AUTO_APPROVE, more reviews

### Scenario 3: Too Many False Positives
**Symptom:** Rejected applicants are paying elsewhere
**Solution:** Increase auto_approve, decrease manual_review
**Effect:** More lenient overall

### Scenario 4: Too Many Defaults
**Symptom:** Accepting too many bad tenants
**Solution:** Decrease auto_approve, increase scrutiny
**Effect:** More strict overall

## Scripts Reference

| Script | Purpose | Runtime |
|--------|---------|---------|
| `demo_three_tier.py` | Demo thresholds & decisions | <1s |
| `train_calibrated_model.py` | Train with proper calibration | 2-5 min |
| `evaluate_three_tier.py` | Cost analysis & metrics | 10-30s |
| `honest_model.py` | Train base model | 2-5 min |

## Emergency Threshold Override

If you need to quickly adjust for a crisis:

```python
# In config/constants.py, change:
AUTO_APPROVE_THRESHOLD = 0.40  # More lenient (was 0.35)
MANUAL_REVIEW_THRESHOLD = 0.75  # Higher bar for reject (was 0.70)
AUTO_REJECT_THRESHOLD = 0.90   # Almost never auto-reject (was 0.85)

# Then restart API
```

## Questions?

**Q: Why 35% threshold?**
A: Optimized for FP cost > FN cost. Empirically reduces FPR to ~22% while keeping recall at 65%.

**Q: Can landlords set their own thresholds?**
A: Yes! Pass `custom_thresholds` in API request.

**Q: What if I don't know my costs?**
A: Start with defaults (FP=$5k, FN=$3k). Refine quarterly with real data.

**Q: Should I auto-reject anyone?**
A: Be very conservative. Even at 85%+ probability, consider manual review unless extreme case (2+ evictions + credit <600).

**Q: How to handle MANUAL_REVIEW queue?**
A: Prioritize by sub-tier. Review MEDIUM-HIGH daily, MEDIUM weekly, LOW-MEDIUM batch process.
