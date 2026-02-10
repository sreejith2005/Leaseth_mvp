import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, ArrowRight, User, Wallet, Briefcase, History, HelpCircle, Building2 } from 'lucide-react'
import Button from '../components/ui/Button'
import { Input, Select, Checkbox, Slider } from '../components/ui/Input'
import { FormRow } from '../components/FormSection'
import LoadingAnalysis from '../components/LoadingAnalysis'
import useForm from '../hooks/useForm'
import { scoreApplicant } from '../services/api'
import { ApplicantInput, ScoringResponse } from '../types'
import { useCurrency } from '../contexts/CurrencyContext'

interface ScoringFormProps {
  onResult: (result: ScoringResponse, input: ApplicantInput) => void
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

const employmentOptions = [
  { value: 'employed', label: 'Employed full-time' },
  { value: 'self-employed', label: 'Self-employed / Freelancer' },
  { value: 'unemployed', label: 'Currently between jobs' },
]

const propertyTypes = [
  { value: 'apartment', label: 'Apartment' },
  { value: 'house', label: 'Independent House' },
  { value: 'condo', label: 'Condo' },
  { value: 'townhouse', label: 'Townhouse' },
  { value: 'studio', label: 'Studio' },
]

const leaseTerms = [
  { value: '6', label: '6 months' },
  { value: '12', label: '12 months' },
  { value: '18', label: '18 months' },
  { value: '24', label: '24 months' },
  { value: '36', label: '36 months' },
]

const monthsToSellOptions = [
  { value: '3', label: '3 months' },
  { value: '6', label: '6 months' },
  { value: '12', label: '12 months' },
  { value: '18', label: '18 months' },
  { value: '24', label: '24 months' },
]

const cities = [
  { value: 'London', label: 'London' },
  { value: 'Dubai', label: 'Dubai' },
  { value: 'New York', label: 'New York' },
  { value: 'Berlin', label: 'Berlin' },
  { value: 'Paris', label: 'Paris' },
  { value: 'Toronto', label: 'Toronto' },
  { value: 'Sydney', label: 'Sydney' },
  { value: 'Singapore', label: 'Singapore' },
  { value: 'Amsterdam', label: 'Amsterdam' },
  { value: 'Zurich', label: 'Zurich' },
  { value: 'Mumbai', label: 'Mumbai' },
  { value: 'São Paulo', label: 'São Paulo' },
  { value: 'Tokyo', label: 'Tokyo' },
  { value: 'Riyadh', label: 'Riyadh' },
  { value: 'Other', label: 'Other' },
]

const steps = [
  { id: 'property', label: 'Your property', icon: Building2 },
  { id: 'tenant', label: 'Your tenant', icon: User },
  { id: 'financial', label: 'Financials', icon: Wallet },
  { id: 'employment', label: 'Verification', icon: Briefcase },
  { id: 'history', label: 'Track record', icon: History },
]

export default function ScoringForm({ onResult, showToast }: ScoringFormProps) {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [activeStep, setActiveStep] = useState(0)
  const { formData, errors, updateField, setFieldTouched, validate } = useForm()
  const { symbol, currencyCode } = useCurrency()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const result = validate()
    if (!result.success || !result.data) {
      showToast('A few fields need your attention', 'error')
      return
    }

    setIsLoading(true)

    try {
      const apiData = { ...result.data, currency: currencyCode }
      const apiResponse = await scoreApplicant(apiData as ApplicantInput)
      onResult(apiResponse, result.data)
      showToast('Offer evaluation complete!', 'success')
      navigate('/results')
    } catch (error) {
      showToast(
        error instanceof Error ? error.message : 'Something went wrong. Give it another go?',
        'error'
      )
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--color-cream)' }}>
        <LoadingAnalysis />
      </div>
    )
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[#faf8f5]/80 border-b border-neutral-200/50">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">Back</span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#7c9a82] flex items-center justify-center">
              <span className="text-white text-xs">L</span>
            </div>
            <span className="text-sm font-medium">Get a Cash Offer</span>
          </div>
          <div className="w-16" />
        </div>
      </header>

      {/* Progress Steps */}
      <div className="border-b border-neutral-200/50 bg-white/30">
        <div className="max-w-3xl mx-auto px-6 py-4">
          <div className="flex justify-between">
            {steps.map((step, i) => (
              <button
                key={step.id}
                onClick={() => setActiveStep(i)}
                className={`flex flex-col items-center gap-2 transition-all duration-200 ${
                  i <= activeStep ? 'opacity-100' : 'opacity-40'
                }`}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200 ${
                  i === activeStep
                    ? 'bg-[#7c9a82] text-white'
                    : i < activeStep
                    ? 'bg-[#7c9a82]/20 text-[#7c9a82]'
                    : 'bg-neutral-100 text-neutral-400'
                }`}>
                  <step.icon className="w-5 h-5" />
                </div>
                <span className={`text-xs hidden sm:block ${
                  i === activeStep ? 'text-neutral-900 font-medium' : 'text-neutral-500'
                }`}>
                  {step.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-6 py-8">
        {/* Header text */}
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
            Tell us about your rental income
          </h1>
          <p className="text-neutral-500">
            We'll evaluate your rental income stream and make you a cash offer. No obligation.
          </p>
        </div>

        {/* Form Sections */}
        <div className="space-y-8">
          {/* Property & Lease Details */}
          <div className={`card transition-all duration-300 ${activeStep === 0 ? 'ring-2 ring-[#7c9a82]/20' : ''}`}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center">
                <Building2 className="w-5 h-5 text-[#7c9a82]" />
              </div>
              <div>
                <h2 className="font-medium">Property & lease details</h2>
                <p className="text-sm text-neutral-500">About your rental property</p>
              </div>
            </div>
            <div className="space-y-6">
              <Input
                label="Property address"
                value={formData.property_address || ''}
                onChange={(e) => updateField('property_address', e.target.value)}
                onFocus={() => setActiveStep(0)}
                placeholder="e.g. 42 Baker Street, London"
              />
              <FormRow>
                <Select
                  label="Property type"
                  options={propertyTypes}
                  value={formData.property_type || ''}
                  onChange={(e) => updateField('property_type', e.target.value as ApplicantInput['property_type'])}
                  onFocus={() => setActiveStep(0)}
                />
                <Select
                  label="City"
                  options={cities}
                  value={formData.location || ''}
                  onChange={(e) => updateField('location', e.target.value)}
                  onFocus={() => setActiveStep(0)}
                />
              </FormRow>
              <FormRow>
                <Input
                  label="Monthly rent"
                  type="number"
                  value={formData.monthly_rent || ''}
                  onChange={(e) => updateField('monthly_rent', parseInt(e.target.value) || 0)}
                  onBlur={() => setFieldTouched('monthly_rent')}
                  onFocus={() => setActiveStep(0)}
                  error={errors.monthly_rent}
                  placeholder="e.g. 2500"
                  prefix={symbol}
                />
                <Input
                  label="Bedrooms"
                  type="number"
                  value={formData.bedrooms || ''}
                  onChange={(e) => updateField('bedrooms', parseInt(e.target.value) || 1)}
                  onFocus={() => setActiveStep(0)}
                  placeholder="e.g. 2"
                />
              </FormRow>
              <FormRow>
                <Select
                  label="Remaining lease term"
                  options={leaseTerms}
                  value={String(formData.lease_term_months || '')}
                  onChange={(e) => updateField('lease_term_months', parseInt(e.target.value))}
                  onFocus={() => setActiveStep(0)}
                />
                <div>
                  <Select
                    label="Months of rent to sell"
                    options={monthsToSellOptions}
                    value={String(formData.months_to_sell || '')}
                    onChange={(e) => updateField('months_to_sell', parseInt(e.target.value))}
                    onFocus={() => setActiveStep(0)}
                  />
                  <p className="text-xs text-neutral-400 mt-1">How many months of future rent you want cash for</p>
                </div>
              </FormRow>
            </div>
          </div>

          {/* Tenant Info */}
          <div className={`card transition-all duration-300 ${activeStep === 1 ? 'ring-2 ring-[#7c9a82]/20' : ''}`}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center">
                <User className="w-5 h-5 text-[#7c9a82]" />
              </div>
              <div>
                <h2 className="font-medium">Current tenant info</h2>
                <p className="text-sm text-neutral-500">Details about your existing tenant</p>
              </div>
            </div>
            <FormRow>
              <Input
                label="Tenant name"
                value={formData.name || ''}
                onChange={(e) => updateField('name', e.target.value)}
                onBlur={() => setFieldTouched('name')}
                onFocus={() => setActiveStep(1)}
                error={errors.name}
                placeholder="Your current tenant's name"
              />
              <Input
                label="Tenant age"
                type="number"
                value={formData.age || ''}
                onChange={(e) => updateField('age', parseInt(e.target.value) || 0)}
                onBlur={() => setFieldTouched('age')}
                onFocus={() => setActiveStep(1)}
                error={errors.age}
                placeholder="e.g. 32"
              />
            </FormRow>
          </div>

          {/* Financial */}
          <div className={`card transition-all duration-300 ${activeStep === 2 ? 'ring-2 ring-[#7c9a82]/20' : ''}`}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center">
                <Wallet className="w-5 h-5 text-[#7c9a82]" />
              </div>
              <div>
                <h2 className="font-medium">Tenant's financial profile</h2>
                <p className="text-sm text-neutral-500">Their ability to continue paying rent</p>
              </div>
            </div>
            <div className="space-y-6">
              <FormRow>
                <Input
                  label="Tenant's monthly income"
                  type="number"
                  value={formData.monthly_income || ''}
                  onChange={(e) => updateField('monthly_income', parseInt(e.target.value) || 0)}
                  onBlur={() => setFieldTouched('monthly_income')}
                  onFocus={() => setActiveStep(2)}
                  error={errors.monthly_income}
                  placeholder="e.g. 5000"
                  prefix={symbol}
                />
                <Input
                  label="Security deposit held"
                  type="number"
                  value={formData.security_deposit || ''}
                  onChange={(e) => updateField('security_deposit', parseInt(e.target.value) || 0)}
                  onFocus={() => setActiveStep(2)}
                  placeholder="Optional"
                  prefix={symbol}
                />
              </FormRow>

              <div>
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-sm font-medium text-neutral-700">Tenant's credit score</span>
                  <div className="group relative">
                    <HelpCircle className="w-4 h-4 text-neutral-400 cursor-help" />
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-neutral-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                      Credit score between 300-850
                    </div>
                  </div>
                </div>
                <Slider
                  min={300}
                  max={850}
                  value={formData.credit_score || 650}
                  onChange={(e) => updateField('credit_score', parseInt(e.target.value))}
                />
                <div className="flex justify-between text-xs text-neutral-400 mt-1">
                  <span>Poor (300)</span>
                  <span className="font-medium text-neutral-700">{formData.credit_score || 650}</span>
                  <span>Excellent (850)</span>
                </div>
              </div>
            </div>
          </div>

          {/* Employment & Verification */}
          <div className={`card transition-all duration-300 ${activeStep === 3 ? 'ring-2 ring-[#7c9a82]/20' : ''}`}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-[#7c9a82]" />
              </div>
              <div>
                <h2 className="font-medium">Employment & verification</h2>
                <p className="text-sm text-neutral-500">Your tenant's employment stability</p>
              </div>
            </div>
            <div className="space-y-6">
              <Select
                label="Tenant's employment status"
                options={employmentOptions}
                value={formData.employment_status || ''}
                onChange={(e) => updateField('employment_status', e.target.value as ApplicantInput['employment_status'])}
                onFocus={() => setActiveStep(3)}
              />

              <div className="flex flex-wrap gap-6 p-4 rounded-xl bg-neutral-50">
                <Checkbox
                  label="Employment verified"
                  sublabel="You've confirmed with their employer"
                  checked={formData.employment_verified || false}
                  onChange={(e) => updateField('employment_verified', e.target.checked)}
                />
                <Checkbox
                  label="Income verified"
                  sublabel="You've seen bank statements or payslips"
                  checked={formData.income_verified || false}
                  onChange={(e) => updateField('income_verified', e.target.checked)}
                />
              </div>
            </div>
          </div>

          {/* Tenant Payment History */}
          <div className={`card transition-all duration-300 ${activeStep === 4 ? 'ring-2 ring-[#7c9a82]/20' : ''}`}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center">
                <History className="w-5 h-5 text-[#7c9a82]" />
              </div>
              <div>
                <h2 className="font-medium">Tenant's payment track record</h2>
                <p className="text-sm text-neutral-500">How reliably they've been paying rent</p>
              </div>
            </div>
            <div className="space-y-6">
              <FormRow>
                <Input
                  label="Years as your tenant"
                  type="number"
                  value={formData.rental_history_years ?? ''}
                  onChange={(e) => updateField('rental_history_years', parseInt(e.target.value) || 0)}
                  onFocus={() => setActiveStep(4)}
                  placeholder="0 if new tenant"
                />
                <Input
                  label="Previous evictions"
                  type="number"
                  value={formData.previous_evictions ?? ''}
                  onChange={(e) => updateField('previous_evictions', parseInt(e.target.value) || 0)}
                  onFocus={() => setActiveStep(4)}
                  placeholder="Hopefully zero!"
                />
              </FormRow>

              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-neutral-700">On-time payment history</span>
                  <span className="text-sm font-medium text-[#7c9a82]">{formData.on_time_payments_percent || 90}%</span>
                </div>
                <Slider
                  min={0}
                  max={100}
                  value={formData.on_time_payments_percent || 90}
                  onChange={(e) => updateField('on_time_payments_percent', parseInt(e.target.value))}
                />
                <div className="flex justify-between text-xs text-neutral-400 mt-1">
                  <span>Never on time</span>
                  <span>Always on time</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-2xl bg-white border border-neutral-100">
          <div className="text-center sm:text-left">
            <p className="font-medium text-neutral-900">Ready for your offer?</p>
            <p className="text-sm text-neutral-500">We'll evaluate your rental income in seconds</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors px-4 py-2"
            >
              Cancel
            </button>
            <Button type="submit" loading={isLoading}>
              Get my cash offer
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>

        {/* Trust note */}
        <p className="text-center text-xs text-neutral-400 mt-6">
          Your data is secure. No obligation — see your offer before deciding.
        </p>
      </form>
    </div>
  )
}
