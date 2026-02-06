# Critical Product Pivot - Leaseth MVP

## Original Misunderstanding
Built for: Landlords screening prospective tenants before signing lease
Output: APPROVE/REJECT tenant application

## Actual Product Vision
Built for: Landlords selling future rental income for upfront cash
Output: Cash offer amount for buying rental payment stream

## Core Concept Explained
Property owners with stable rental income sometimes need immediate cash but don't want debt. Leaseth buys their future rental payments at a discount. Owner gets cash now, keeps property ownership, no loan created.

**Example:**
- Landlord receives $1,500/month rent consistently
- Needs $15,000 now
- Leaseth offers $14,000 cash for next 12 months of rent ($18,000 total value)
- Landlord gets money upfront, no debt, still owns property
- Leaseth collects the $1,500/month for next year

## AI Scoring Purpose
**NOT** evaluating whether to rent to someone.
**IS** evaluating reliability/predictability of rental income stream to determine:
- Whether to make an offer at all (if too risky = reject)
- How much discount to apply (lower risk = better offer)

Risk factors that matter:
- Tenant payment history
- Tenant employment stability
- Property cash flow consistency
- Lease term remaining
- Market stability

## Frontend Rebuild Required

**Landing Page:**
- Value prop: "Get cash now by selling your future rent payments"
- No debt, keep property ownership
- Fast liquidity for property owners

**Input Form:**
Landlord enters:
- Property details (address, type, market data)
- Current tenant information (NOT prospective - this is existing renter)
- Rental agreement details (monthly rent, lease term, payment history)
- Financial verification data

**Output Display:**
Primary result is **offer amount**, not approve/reject:

**Approved Flow:**
- "We can offer you $X upfront"
- "For your next Y months of rent payments"
- Breakdown: Total rental value vs offered amount vs discount
- "Rental income reliability score: Z/100"
- Accept offer CTA

**Rejected Flow:**
- "Unable to make an offer at this time"
- Reason: Risk score too high
- Factors affecting decision
- Suggestions to improve eligibility

**Dashboard Changes:**
- Show property owners' submissions
- Track offers made vs accepted
- Portfolio view of income streams purchased
- Risk distribution of offers

## Backend Compatibility
Current AI model likely still works - it evaluates tenant reliability. But interpretation changes:
- High risk score = low/no offer (risky income stream)
- Low risk score = better offer (reliable income stream)

May need to add:
- Offer calculation logic based on risk score
- Discount rate determination
- Cash flow projection
- Property valuation factors

## MVP Priority
Elitay confirms: Only AI scoring accuracy matters for MVP. Design, marketing, extra features are secondary. Focus on:
1. Accurate risk assessment of rental income reliability
2. Clear offer/rejection output
3. Simple, functional flow

Get the algorithm and decision logic right. Polish later.
