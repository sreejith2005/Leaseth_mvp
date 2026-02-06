import { useState, useCallback } from 'react'
import { ApplicantInput } from '../types'
import { validateField, validateForm, generateApplicantId } from '../utils/validation'

type FormData = Partial<ApplicantInput>
type FormErrors = Record<string, string>

const defaultFormData: FormData = {
  applicant_id: generateApplicantId(),
  name: '',
  age: 30,
  monthly_income: 5000,
  credit_score: 650,
  monthly_rent: 1500,
  security_deposit: 1500,
  employment_status: 'employed',
  employment_verified: false,
  income_verified: false,
  rental_history_years: 2,
  previous_evictions: 0,
  on_time_payments_percent: 90,
  late_payments_count: 0,
  lease_term_months: 12,
  months_to_sell: 12,
  bedrooms: 2,
  property_type: 'apartment',
  location: '',
  property_address: '',
}

export function useForm(initialData: FormData = defaultFormData) {
  const [formData, setFormData] = useState<FormData>({
    ...defaultFormData,
    ...initialData,
    applicant_id: generateApplicantId(),
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [touched, setTouched] = useState<Set<string>>(new Set())

  const updateField = useCallback(<K extends keyof ApplicantInput>(
    field: K,
    value: ApplicantInput[K]
  ) => {
    setFormData(prev => ({ ...prev, [field]: value }))

    // Only validate if field has been touched
    if (touched.has(field)) {
      const error = validateField(field, value, formData)
      setErrors(prev => {
        if (error) {
          return { ...prev, [field]: error }
        }
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }, [formData, touched])

  const setFieldTouched = useCallback((field: string) => {
    setTouched(prev => new Set(prev).add(field))

    // Validate when field is touched
    const value = formData[field as keyof FormData]
    const error = validateField(field as keyof ApplicantInput, value, formData)
    if (error) {
      setErrors(prev => ({ ...prev, [field]: error }))
    }
  }, [formData])

  const validate = useCallback(() => {
    const result = validateForm(formData)
    if (!result.success) {
      setErrors(result.errors)
      // Mark all fields as touched
      const allFields = Object.keys(formData) as string[]
      setTouched(new Set(allFields))
    }
    return result
  }, [formData])

  const reset = useCallback(() => {
    setFormData({
      ...defaultFormData,
      applicant_id: generateApplicantId(),
    })
    setErrors({})
    setTouched(new Set())
  }, [])

  const isValid = Object.keys(errors).length === 0

  return {
    formData,
    errors,
    touched,
    isValid,
    updateField,
    setFieldTouched,
    validate,
    reset,
    setFormData,
  }
}

export default useForm
