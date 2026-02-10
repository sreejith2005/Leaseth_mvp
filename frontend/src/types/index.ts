// ============================================================
// Leaseth Rental Income Advance - Type Definitions
// ============================================================

/**
 * Property submission input for rental income advance evaluation.
 * Landlord submits details about their property and existing tenant
 * to receive a cash offer for future rental payments.
 */
export interface ApplicantInput {
  applicant_id: string;          // Submission ID
  name: string;                  // Current tenant name
  age: number;
  monthly_income: number;        // Tenant's monthly income
  credit_score: number;          // Tenant's credit score
  monthly_rent: number;          // Monthly rent amount
  security_deposit?: number;
  employment_status: 'employed' | 'self-employed' | 'unemployed';
  employment_verified: boolean;
  income_verified: boolean;
  rental_history_years: number;  // How long tenant has been renting
  previous_evictions: number;
  on_time_payments_percent: number;
  late_payments_count: number;
  lease_term_months: number;     // Remaining lease term
  months_to_sell: number;        // Months of rent landlord wants to sell (1-60)
  bedrooms: number;
  property_type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'studio';
  location: string;
  property_address: string;      // Property address
  currency?: string;             // ISO 4217 currency code (e.g. "USD", "EUR")
}

/**
 * Response from scoring API with offer details.
 * Includes both risk assessment and cash offer calculation.
 */
export interface ScoringResponse {
  applicant_id: string;
  
  // Risk assessment (internal)
  risk_score: number;
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation: string;
  confidence: number;
  reasoning: string;
  processing_time_ms?: number;
  success?: boolean;
  default_probability?: number;
  
  // Offer details (primary output)
  reliability_score: number;       // 0-100 (higher = more reliable income)
  offer_status: 'OFFERED' | 'NO_OFFER';
  offer_amount: number;            // Cash offer amount
  gross_rental_value: number;      // Total value of rent stream
  discount_rate: number;           // Discount percentage (0-1)
  discount_amount: number;         // Amount discounted
  months_purchased: number;        // Months of rent being purchased
}

/**
 * Stored submission with results (for dashboard/history).
 */
export interface StoredApplicant {
  id: string;
  input: Partial<ApplicantInput> & { name?: string; location?: string; applicant_id?: string };
  result: ScoringResponse;
  scored_at: string;
}

export type RiskCategory = 'LOW' | 'MEDIUM' | 'HIGH';
export type OfferStatus = 'OFFERED' | 'NO_OFFER';
export type ReliabilityCategory = 'HIGH' | 'MEDIUM' | 'LOW';

/** @deprecated - kept for backward compat with old components */
export type Recommendation = string;

/**
 * Helper to get reliability category from score
 */
export function getReliabilityCategory(score: number): ReliabilityCategory {
  if (score >= 70) return 'HIGH'
  if (score >= 40) return 'MEDIUM'
  return 'LOW'
}
