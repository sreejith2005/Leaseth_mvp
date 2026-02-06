import { useNavigate, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, Download, Share2, CheckCircle, XCircle, Lightbulb, TrendingUp, TrendingDown, DollarSign, Calendar, Percent, Shield } from 'lucide-react'
import { ScoringResponse, ApplicantInput, getReliabilityCategory } from '../types'
import { useCurrency } from '../contexts/CurrencyContext'

interface ResultsProps {
  result: ScoringResponse | null
  input: ApplicantInput | null
}

function getReliabilityColor(score: number) {
  if (score >= 70) return { text: 'text-emerald-600', bg: 'bg-emerald-100' }
  if (score >= 40) return { text: 'text-amber-600', bg: 'bg-amber-100' }
  return { text: 'text-red-600', bg: 'bg-red-100' }
}

export default function Results({ result, input }: ResultsProps) {
  const navigate = useNavigate()
  const [showConfetti, setShowConfetti] = useState(false)
  const { formatCurrency } = useCurrency()

  useEffect(() => {
    if (!result) {
      navigate('/score')
      return
    }
    // Show confetti for approved offers
    if (result.offer_status === 'OFFERED' && result.reliability_score >= 60) {
      setShowConfetti(true)
      setTimeout(() => setShowConfetti(false), 3000)
    }
  }, [result, navigate])

  if (!result || !input) {
    return null
  }

  const reliabilityColors = getReliabilityColor(result.reliability_score)
  const reliabilityCategory = getReliabilityCategory(result.reliability_score)
  const isOffered = result.offer_status === 'OFFERED'

  // Determine strengths and concerns about this income stream
  const strengths: string[] = []
  const concerns: string[] = []

  if (input.credit_score >= 700) strengths.push('Tenant has strong credit score')
  else if (input.credit_score < 600) concerns.push('Tenant has low credit score')

  const rentToIncome = Math.round((input.monthly_rent / input.monthly_income) * 100)
  if (rentToIncome <= 30) strengths.push('Healthy rent-to-income ratio')
  else if (rentToIncome > 40) concerns.push('High rent burden on tenant')

  if (input.previous_evictions === 0) strengths.push('Clean eviction record')
  else concerns.push(`${input.previous_evictions} previous eviction(s)`)

  if (input.employment_verified && input.income_verified) strengths.push('Employment & income verified')
  else if (!input.employment_verified && !input.income_verified) concerns.push('No employment/income verification')

  if (input.on_time_payments_percent >= 90) strengths.push('Excellent payment track record')
  else if (input.on_time_payments_percent < 70) concerns.push('Inconsistent payment history')

  if (input.rental_history_years >= 3) strengths.push('Long-term stable tenant')
  else if (input.rental_history_years === 0) concerns.push('New tenant — no rental history')

  if (input.lease_term_months >= 12) strengths.push('Strong lease term remaining')
  else if (input.lease_term_months < 6) concerns.push('Short remaining lease')

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* Confetti effect for good offers */}
      {showConfetti && (
        <div className="fixed inset-0 pointer-events-none z-50 overflow-hidden">
          {[...Array(50)].map((_, i) => (
            <div
              key={i}
              className="absolute w-3 h-3 rounded-full animate-bounce"
              style={{
                left: `${Math.random() * 100}%`,
                top: '-20px',
                backgroundColor: ['#7c9a82', '#c4704f', '#d4c5b0', '#faf8f5'][Math.floor(Math.random() * 4)],
                animation: `fall ${2 + Math.random() * 2}s ease-out forwards`,
                animationDelay: `${Math.random() * 0.5}s`
              }}
            />
          ))}
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[#faf8f5]/80 border-b border-neutral-200/50">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/score" className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm">New submission</span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#7c9a82] flex items-center justify-center">
              <span className="text-white text-xs">L</span>
            </div>
            <span className="text-sm font-medium">Your Offer</span>
          </div>
          <div className="flex gap-2">
            <button className="p-2 rounded-lg hover:bg-neutral-100 transition-colors text-neutral-500">
              <Share2 className="w-4 h-4" />
            </button>
            <button className="p-2 rounded-lg hover:bg-neutral-100 transition-colors text-neutral-500">
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-8 md:py-12">

        {isOffered ? (
          <>
            {/* ============================================================ */}
            {/* OFFERED: Show cash offer as hero                             */}
            {/* ============================================================ */}

            {/* Hero Offer Section */}
            <div className="card p-8 md:p-12 mb-8 text-center relative overflow-hidden">
              <div
                className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-10 blob"
                style={{ backgroundColor: '#7c9a82' }}
              />

              <div className="relative z-10">
                <p className="text-neutral-500 mb-1">Cash offer for your rental income</p>
                <p className="text-sm text-neutral-400 mb-8">
                  Property: {input.property_address || input.location} · Tenant: {input.name}
                </p>

                <div className="mb-2">
                  <span
                    className="text-7xl md:text-8xl font-light text-emerald-600"
                    style={{ fontFamily: 'DM Serif Display, serif' }}
                  >
                    {formatCurrency(result.offer_amount)}
                  </span>
                </div>
                <p className="text-neutral-500 mb-8">
                  Upfront cash for {result.months_purchased} months of rental income
                </p>

                <div className="flex items-center justify-center gap-4 flex-wrap">
                  <span className={`px-4 py-2 rounded-full text-sm font-medium ${reliabilityColors.bg} ${reliabilityColors.text}`}>
                    {reliabilityCategory} reliability
                  </span>
                  <span className="px-4 py-2 rounded-full text-sm font-medium border bg-emerald-50 text-emerald-700 border-emerald-200">
                    <CheckCircle className="w-4 h-4 inline mr-2" />
                    Offer available
                  </span>
                </div>
              </div>
            </div>

            {/* Offer Breakdown */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="card p-5 text-center">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center mx-auto mb-3">
                  <DollarSign className="w-5 h-5 text-emerald-600" />
                </div>
                <p className="text-2xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                  {formatCurrency(result.gross_rental_value)}
                </p>
                <p className="text-xs text-neutral-500">Total Rental Value</p>
              </div>
              <div className="card p-5 text-center">
                <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center mx-auto mb-3">
                  <Percent className="w-5 h-5 text-amber-600" />
                </div>
                <p className="text-2xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                  {(result.discount_rate * 100).toFixed(1)}%
                </p>
                <p className="text-xs text-neutral-500">Discount Rate</p>
              </div>
              <div className="card p-5 text-center">
                <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center mx-auto mb-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                </div>
                <p className="text-2xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                  {result.months_purchased}
                </p>
                <p className="text-xs text-neutral-500">Months Purchased</p>
              </div>
              <div className="card p-5 text-center">
                <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/10 flex items-center justify-center mx-auto mb-3">
                  <Shield className="w-5 h-5 text-[#7c9a82]" />
                </div>
                <p className={`text-2xl font-light mb-1 ${reliabilityColors.text}`} style={{ fontFamily: 'DM Serif Display, serif' }}>
                  {result.reliability_score}
                </p>
                <p className="text-xs text-neutral-500">Reliability Score</p>
              </div>
            </div>

            {/* Deal Summary Card */}
            <div className="card p-6 mb-8 border-l-4 border-emerald-300">
              <h3 className="font-medium text-lg mb-4" style={{ fontFamily: 'DM Serif Display, serif' }}>
                How this works
              </h3>
              <div className="space-y-3 text-sm text-neutral-600">
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span>Your monthly rent</span>
                  <span className="font-medium">{formatCurrency(input.monthly_rent)}/month</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span>Months of rent you're selling</span>
                  <span className="font-medium">{result.months_purchased} months</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span>Total rental value</span>
                  <span className="font-medium">{formatCurrency(result.gross_rental_value)}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-neutral-100">
                  <span>Discount applied ({(result.discount_rate * 100).toFixed(1)}%)</span>
                  <span className="font-medium text-amber-600">-{formatCurrency(result.discount_amount)}</span>
                </div>
                <div className="flex justify-between py-3 text-base font-medium text-emerald-700 bg-emerald-50 -mx-2 px-4 rounded-lg">
                  <span>You receive upfront</span>
                  <span>{formatCurrency(result.offer_amount)}</span>
                </div>
              </div>
              <p className="text-xs text-neutral-400 mt-4">
                You keep property ownership. No debt created. Leaseth collects the monthly rent for the agreed period.
              </p>
            </div>

            {/* Accept Offer CTA */}
            <div className="card p-6 mb-8 text-center bg-gradient-to-r from-emerald-50 to-[#7c9a82]/10 border border-emerald-200">
              <h3 className="text-xl font-medium mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
                Ready to get your cash?
              </h3>
              <p className="text-neutral-600 text-sm mb-6">This offer is valid for 48 hours</p>
              <button className="btn-primary px-10 py-4 text-lg">
                Accept Offer
                <ArrowRight className="w-5 h-5 ml-2" />
              </button>
            </div>
          </>
        ) : (
          <>
            {/* ============================================================ */}
            {/* NO OFFER: Show rejection with reasoning                      */}
            {/* ============================================================ */}

            <div className="card p-8 md:p-12 mb-8 text-center relative overflow-hidden">
              <div
                className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-10 blob"
                style={{ backgroundColor: '#c4704f' }}
              />

              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-red-100 flex items-center justify-center mx-auto mb-6">
                  <XCircle className="w-8 h-8 text-red-500" />
                </div>
                <h1 className="text-2xl md:text-3xl mb-4" style={{ fontFamily: 'DM Serif Display, serif' }}>
                  Unable to make an offer
                </h1>
                <p className="text-neutral-600 mb-4 max-w-md mx-auto">
                  {result.reasoning}
                </p>
                <p className="text-sm text-neutral-400">
                  Reliability score: {result.reliability_score}/100 (minimum 40 required)
                </p>
              </div>
            </div>
          </>
        )}

        {/* Strengths & Concerns */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="font-medium" style={{ fontFamily: 'DM Serif Display, serif' }}>Income stream strengths</h3>
            </div>
            {strengths.length > 0 ? (
              <ul className="space-y-2">
                {strengths.map((s, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-neutral-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                    {s}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-neutral-400 italic">No major strengths identified</p>
            )}
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-amber-600" />
              </div>
              <h3 className="font-medium" style={{ fontFamily: 'DM Serif Display, serif' }}>Risk factors</h3>
            </div>
            {concerns.length > 0 ? (
              <ul className="space-y-2">
                {concerns.map((c, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-neutral-600">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                    {c}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-neutral-400 italic">No major concerns</p>
            )}
          </div>
        </div>

        {/* Tenant & Property Details */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card p-6">
            <h3 className="text-xs uppercase tracking-wide text-neutral-400 mb-4">Tenant Details</h3>
            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Tenant name</span>
                <span className="font-medium">{input.name}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Monthly income</span>
                <span className="font-medium">{formatCurrency(input.monthly_income)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Credit score</span>
                <span className="font-medium">{input.credit_score}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Employment</span>
                <span className="font-medium capitalize">{input.employment_status.replace('-', ' ')}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-neutral-600">Payment history</span>
                <span className="font-medium">{input.on_time_payments_percent}% on-time</span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-xs uppercase tracking-wide text-neutral-400 mb-4">Property & Lease</h3>
            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Monthly rent</span>
                <span className="font-medium">{formatCurrency(input.monthly_rent)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Property type</span>
                <span className="font-medium capitalize">{input.property_type}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Location</span>
                <span className="font-medium">{input.location}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Remaining lease</span>
                <span className="font-medium">{input.lease_term_months} months</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-neutral-600">Years as tenant</span>
                <span className="font-medium">{input.rental_history_years}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Pro tip */}
        <div className="card p-6 mb-8 bg-[#7c9a82]/5 border border-[#7c9a82]/20">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-xl bg-[#7c9a82]/20 flex items-center justify-center flex-shrink-0">
              <Lightbulb className="w-5 h-5 text-[#7c9a82]" />
            </div>
            <div>
              <h3 className="font-medium text-neutral-900 mb-1">Tips to improve your offer</h3>
              <p className="text-sm text-neutral-600">
                {isOffered
                  ? result.reliability_score >= 70
                    ? "Great income stream! Consider selling more months for a larger lump sum. Longer lease terms also improve your rate."
                    : "Get tenant's employment and income verified to boost your reliability score and receive a better rate."
                  : "Ensure your tenant has verified employment and income. A longer lease term and clean payment history significantly improve eligibility."}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-2xl bg-white border border-neutral-100">
          <div className="text-center sm:text-left">
            <p className="font-medium text-neutral-900">Want to try different terms?</p>
            <p className="text-sm text-neutral-500">Submit another property or adjust the months</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/score')}
              className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors px-4 py-2"
            >
              New submission
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-primary"
            >
              View all offers
              <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </main>

      {/* CSS for confetti animation */}
      <style>{`
        @keyframes fall {
          0% {
            transform: translateY(0) rotate(0deg);
            opacity: 1;
          }
          100% {
            transform: translateY(100vh) rotate(720deg);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  )
}
