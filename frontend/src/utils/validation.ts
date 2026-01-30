import { z } from 'zod'

// Base schema without refinement for single-field validation
const baseApplicantSchema = z.object({
  applicant_id: z.string().min(1, 'Applicant ID is required'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  age: z.number().min(18, 'Must be at least 18 years old').max(120, 'Invalid age'),
  monthly_income: z.number().min(0, 'Income cannot be negative'),
  credit_score: z.number().min(300, 'Credit score must be at least 300').max(850, 'Credit score cannot exceed 850'),
  monthly_rent: z.number().min(0, 'Rent cannot be negative'),
  security_deposit: z.number().min(0).optional(),
  employment_status: z.enum(['employed', 'self-employed', 'unemployed']),
  employment_verified: z.boolean(),
  income_verified: z.boolean(),
  rental_history_years: z.number().min(0, 'Cannot be negative'),
  previous_evictions: z.number().min(0, 'Cannot be negative'),
  on_time_payments_percent: z.number().min(0).max(100),
  late_payments_count: z.number().min(0, 'Cannot be negative'),
  lease_term_months: z.number().min(1),
  bedrooms: z.number().min(1).max(10),
  property_type: z.enum(['apartment', 'house', 'condo', 'townhouse', 'studio']),
  location: z.string().min(1, 'Location is required'),
})

// Full schema with cross-field validation
export const applicantSchema = baseApplicantSchema.refine(
  (data) => data.monthly_rent <= data.monthly_income * 2,
  {
    message: 'Monthly rent should not exceed 2x monthly income',
    path: ['monthly_rent'],
  }
)

export type ApplicantFormData = z.infer<typeof applicantSchema>

// Field schemas for individual validation
const fieldSchemas: Record<string, z.ZodTypeAny> = {
  applicant_id: z.string().min(1, 'Applicant ID is required'),
  name: z.string().min(2, 'Name must be at least 2 characters'),
  age: z.number().min(18, 'Must be at least 18 years old').max(120, 'Invalid age'),
  monthly_income: z.number().min(0, 'Income cannot be negative'),
  credit_score: z.number().min(300, 'Credit score must be at least 300').max(850, 'Credit score cannot exceed 850'),
  monthly_rent: z.number().min(0, 'Rent cannot be negative'),
  security_deposit: z.number().min(0).optional(),
  employment_status: z.enum(['employed', 'self-employed', 'unemployed']),
  employment_verified: z.boolean(),
  income_verified: z.boolean(),
  rental_history_years: z.number().min(0, 'Cannot be negative'),
  previous_evictions: z.number().min(0, 'Cannot be negative'),
  on_time_payments_percent: z.number().min(0).max(100),
  late_payments_count: z.number().min(0, 'Cannot be negative'),
  lease_term_months: z.number().min(1),
  bedrooms: z.number().min(1).max(10),
  property_type: z.enum(['apartment', 'house', 'condo', 'townhouse', 'studio']),
  location: z.string().min(1, 'Location is required'),
}

export function validateField(
  field: keyof ApplicantFormData,
  value: unknown,
  formData: Partial<ApplicantFormData>
): string | null {
  try {
    const schema = fieldSchemas[field]
    if (schema) {
      schema.parse(value)
    }

    // Additional cross-field validation for rent vs income
    if (field === 'monthly_rent' && formData.monthly_income !== undefined) {
      const rent = value as number
      if (rent > (formData.monthly_income || 0) * 2) {
        return 'Monthly rent should not exceed 2x monthly income'
      }
    }

    return null
  } catch (error) {
    if (error instanceof z.ZodError) {
      return error.errors[0]?.message || 'Invalid value'
    }
    return 'Invalid value'
  }
}

export function validateForm(data: unknown): { success: boolean; errors: Record<string, string>; data?: ApplicantFormData } {
  try {
    const validData = applicantSchema.parse(data)
    return { success: true, errors: {}, data: validData }
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {}
      error.errors.forEach((err) => {
        const path = err.path.join('.')
        errors[path] = err.message
      })
      return { success: false, errors }
    }
    return { success: false, errors: { _form: 'Validation failed' } }
  }
}

export function generateApplicantId(): string {
  return `APP-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`
}
