"""
Offer Calculator for Leaseth Rental Income Advance Platform

Converts a reliability score (inverted from risk score) into a cash offer
for purchasing future rental income streams from property owners.

Core concept:
- Landlord receives $X/month rent consistently
- Leaseth offers upfront cash for next N months of rent at a discount
- Lower reliability = higher discount (riskier income stream)
- Higher reliability = better offer for the landlord
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class OfferBreakdown:
    """Detailed breakdown of a cash offer"""
    offer_amount: float          # Net cash offered to landlord
    gross_rental_value: float    # Total value of future rent payments
    discount_rate: float         # Total discount percentage (0-1)
    discount_amount: float       # Dollar amount of discount
    monthly_rent: float          # Monthly rent amount
    months: int                  # Number of months being purchased
    reliability_score: int       # 0-100 (higher = more reliable)
    offer_status: str            # OFFERED or NO_OFFER


# Minimum reliability score to make an offer
MIN_RELIABILITY_THRESHOLD = 40

# Base discount rate for a perfect (100) reliability score
BASE_DISCOUNT_RATE = 0.10  # 10%

# Additional risk premium per reliability point below 100
RISK_PREMIUM_PER_POINT = 0.004  # 0.4% per point below 100

# Maximum discount rate cap
MAX_DISCOUNT_RATE = 0.45  # 45%

# Property type risk adjustments
PROPERTY_TYPE_ADJUSTMENTS = {
    'apartment': 0.00,
    'house': -0.02,       # Houses = more stable, better rate for landlord
    'condo': 0.01,
    'townhouse': -0.01,
    'studio': 0.02,
    'villa': -0.02,
}

# Lease term adjustments (longer remaining lease = less risk)
def _lease_term_adjustment(months: int) -> float:
    """Longer lease terms reduce risk"""
    if months >= 24:
        return -0.03  # 3% discount reduction for 2+ year leases
    elif months >= 12:
        return -0.01  # 1% reduction for 1+ year
    elif months >= 6:
        return 0.0
    else:
        return 0.03   # Short lease = more risk


def calculate_offer(
    monthly_rent: float,
    months_to_sell: int,
    reliability_score: int,
    property_type: str = "apartment",
    lease_term_months: int = 12,
    credit_score: int = 650,
    on_time_payments_pct: float = 90.0,
) -> OfferBreakdown:
    """
    Calculate a cash offer for purchasing a rental income stream.

    Args:
        monthly_rent: Current monthly rent amount
        months_to_sell: Number of months of rent the landlord wants to sell
        reliability_score: 0-100 score (inverted from risk_score: 100 - risk_score)
        property_type: Type of rental property
        lease_term_months: Remaining months on tenant's lease
        credit_score: Tenant's credit score
        on_time_payments_pct: Tenant's on-time payment percentage

    Returns:
        OfferBreakdown with full offer details
    """
    gross_value = monthly_rent * months_to_sell

    # Check minimum threshold
    if reliability_score < MIN_RELIABILITY_THRESHOLD:
        logger.info(f"Reliability {reliability_score} below threshold {MIN_RELIABILITY_THRESHOLD} - NO_OFFER")
        return OfferBreakdown(
            offer_amount=0,
            gross_rental_value=gross_value,
            discount_rate=0,
            discount_amount=0,
            monthly_rent=monthly_rent,
            months=months_to_sell,
            reliability_score=reliability_score,
            offer_status="NO_OFFER",
        )

    # 1. Base discount from reliability score
    risk_points = 100 - reliability_score
    base_discount = BASE_DISCOUNT_RATE + (risk_points * RISK_PREMIUM_PER_POINT)

    # 2. Property type adjustment
    prop_adj = PROPERTY_TYPE_ADJUSTMENTS.get(property_type.lower(), 0.0)
    base_discount += prop_adj

    # 3. Lease term adjustment
    lease_adj = _lease_term_adjustment(lease_term_months)
    base_discount += lease_adj

    # 4. Payment history bonus
    if on_time_payments_pct >= 95:
        base_discount -= 0.02  # Excellent history = 2% better rate
    elif on_time_payments_pct >= 85:
        base_discount -= 0.01

    # 5. Credit score bonus
    if credit_score >= 750:
        base_discount -= 0.02
    elif credit_score >= 700:
        base_discount -= 0.01

    # 6. Volume bonus for selling more months
    if months_to_sell >= 18:
        base_discount -= 0.01  # Small bonus for larger deals
    elif months_to_sell <= 3:
        base_discount += 0.02  # Premium for very short term

    # Cap discount rate
    final_discount = max(0.05, min(MAX_DISCOUNT_RATE, base_discount))

    # Calculate offer
    discount_amount = gross_value * final_discount
    offer_amount = gross_value - discount_amount

    logger.info(
        f"Offer calculated: reliability={reliability_score}, "
        f"gross={gross_value:,.0f}, discount={final_discount:.1%}, "
        f"offer={offer_amount:,.0f}"
    )

    return OfferBreakdown(
        offer_amount=round(offer_amount, 2),
        gross_rental_value=gross_value,
        discount_rate=round(final_discount, 4),
        discount_amount=round(discount_amount, 2),
        monthly_rent=monthly_rent,
        months=months_to_sell,
        reliability_score=reliability_score,
        offer_status="OFFERED",
    )
