export interface ApplicantInput {
  applicant_id: string;
  name: string;
  age: number;
  monthly_income: number;
  credit_score: number;
  monthly_rent: number;
  security_deposit?: number;
  employment_status: 'employed' | 'self-employed' | 'unemployed';
  employment_verified: boolean;
  income_verified: boolean;
  rental_history_years: number;
  previous_evictions: number;
  on_time_payments_percent: number;
  late_payments_count: number;
  lease_term_months: number;
  bedrooms: number;
  property_type: 'apartment' | 'house' | 'condo' | 'townhouse' | 'studio';
  location: string;
}

export interface ScoringResponse {
  applicant_id: string;
  risk_score: number;
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH';
  recommendation: string; // Can be APPROVE, MANUAL_REVIEW, REJECT, or variations like "MANUAL_REVIEW (Lean Approve)"
  confidence: number;
  reasoning: string;
  processing_time_ms?: number; // Optional - may not be present in all responses
  success?: boolean; // Backend returns this
  default_probability?: number; // Backend returns this
}

export interface StoredApplicant {
  id: string;
  input: Partial<ApplicantInput> & { name?: string; location?: string; applicant_id?: string };
  result: ScoringResponse;
  scored_at: string;
}

export type RiskCategory = 'LOW' | 'MEDIUM' | 'HIGH';
export type Recommendation = 'APPROVE' | 'MANUAL_REVIEW' | 'REJECT' | string;
