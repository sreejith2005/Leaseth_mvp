import { useNavigate, Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, Download, Share2, CheckCircle, AlertTriangle, XCircle, Lightbulb, TrendingUp, TrendingDown } from 'lucide-react'
import { ScoringResponse, ApplicantInput } from '../types'

interface ResultsProps {
  result: ScoringResponse | null
  input: ApplicantInput | null
}

function getRecommendationConfig(rec: string) {
  if (rec === 'APPROVE') {
    return {
      label: 'Approve',
      description: 'This applicant looks good to go',
      icon: CheckCircle,
      color: 'emerald',
      bgClass: 'bg-emerald-50',
      textClass: 'text-emerald-700',
      borderClass: 'border-emerald-200'
    }
  }
  if (rec.startsWith('MANUAL_REVIEW')) {
    return {
      label: 'Review needed',
      description: 'Worth a closer look before deciding',
      icon: AlertTriangle,
      color: 'amber',
      bgClass: 'bg-amber-50',
      textClass: 'text-amber-700',
      borderClass: 'border-amber-200'
    }
  }
  return {
    label: 'Decline',
    description: 'High risk signals detected',
    icon: XCircle,
    color: 'red',
    bgClass: 'bg-red-50',
    textClass: 'text-red-700',
    borderClass: 'border-red-200'
  }
}

function getRiskColor(category: string) {
  if (category === 'LOW') return { text: 'text-emerald-600', bg: 'bg-emerald-100' }
  if (category === 'MEDIUM') return { text: 'text-amber-600', bg: 'bg-amber-100' }
  return { text: 'text-red-600', bg: 'bg-red-100' }
}

export default function Results({ result, input }: ResultsProps) {
  const navigate = useNavigate()
  const [showConfetti, setShowConfetti] = useState(false)

  useEffect(() => {
    if (!result) {
      navigate('/score')
      return
    }
    // Show confetti for low-risk approved tenants
    if (result.risk_category === 'LOW' && result.recommendation === 'APPROVE') {
      setShowConfetti(true)
      setTimeout(() => setShowConfetti(false), 3000)
    }
  }, [result, navigate])

  if (!result || !input) {
    return null
  }

  const rentToIncome = Math.round((input.monthly_rent / input.monthly_income) * 100)
  const recConfig = getRecommendationConfig(result.recommendation)
  const riskColors = getRiskColor(result.risk_category)
  const RecIcon = recConfig.icon

  // Determine what's good and what's concerning
  const strengths: string[] = []
  const concerns: string[] = []

  if (input.credit_score >= 700) strengths.push('Strong credit score')
  else if (input.credit_score < 600) concerns.push('Low credit score')

  if (rentToIncome <= 30) strengths.push('Healthy rent-to-income ratio')
  else if (rentToIncome > 40) concerns.push('High rent-to-income ratio')

  if (input.previous_evictions === 0) strengths.push('Clean eviction record')
  else concerns.push(`${input.previous_evictions} previous eviction(s)`)

  if (input.employment_verified && input.income_verified) strengths.push('Verified employment & income')
  else if (!input.employment_verified && !input.income_verified) concerns.push('Unverified employment/income')

  if (input.on_time_payments_percent >= 90) strengths.push('Excellent payment history')
  else if (input.on_time_payments_percent < 70) concerns.push('Inconsistent payment history')

  if (input.rental_history_years >= 3) strengths.push('Experienced renter')
  else if (input.rental_history_years === 0) concerns.push('First-time renter')

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* Confetti effect for good results */}
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
            <span className="text-sm">New assessment</span>
          </Link>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-[#7c9a82] flex items-center justify-center">
              <span className="text-white text-xs">L</span>
            </div>
            <span className="text-sm font-medium">Results</span>
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
        {/* Hero Score Section */}
        <div className="card p-8 md:p-12 mb-8 text-center relative overflow-hidden">
          {/* Decorative blob */}
          <div
            className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-10 blob"
            style={{ backgroundColor: result.risk_category === 'LOW' ? '#7c9a82' : result.risk_category === 'MEDIUM' ? '#d4a574' : '#c4704f' }}
          />

          <div className="relative z-10">
            <p className="text-neutral-500 mb-2">Assessment for</p>
            <h1 className="text-2xl md:text-3xl mb-8" style={{ fontFamily: 'DM Serif Display, serif' }}>
              {input.name}
            </h1>

            <div className="mb-8">
              <div
                className={`text-8xl md:text-9xl font-light ${riskColors.text}`}
                style={{ fontFamily: 'DM Serif Display, serif' }}
              >
                {result.risk_score}
              </div>
              <p className="text-neutral-500 mt-2">Risk Score (lower is better)</p>
            </div>

            <div className="flex items-center justify-center gap-4 flex-wrap">
              <span className={`px-4 py-2 rounded-full text-sm font-medium ${riskColors.bg} ${riskColors.text}`}>
                {result.risk_category.toLowerCase()} risk
              </span>
              <span className={`px-4 py-2 rounded-full text-sm font-medium border ${recConfig.bgClass} ${recConfig.textClass} ${recConfig.borderClass}`}>
                <RecIcon className="w-4 h-4 inline mr-2" />
                {recConfig.label}
              </span>
            </div>
          </div>
        </div>

        {/* Recommendation Card */}
        <div className={`card p-6 mb-8 border-l-4 ${recConfig.borderClass}`}>
          <div className="flex items-start gap-4">
            <div className={`w-12 h-12 rounded-xl ${recConfig.bgClass} flex items-center justify-center flex-shrink-0`}>
              <RecIcon className={`w-6 h-6 ${recConfig.textClass}`} />
            </div>
            <div>
              <h2 className="font-medium text-lg mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                {recConfig.label}
              </h2>
              <p className="text-neutral-600">{result.reasoning}</p>
            </div>
          </div>
        </div>

        {/* Strengths & Concerns */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Strengths */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-emerald-600" />
              </div>
              <h3 className="font-medium" style={{ fontFamily: 'DM Serif Display, serif' }}>What's working</h3>
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

          {/* Concerns */}
          <div className="card p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-amber-600" />
              </div>
              <h3 className="font-medium" style={{ fontFamily: 'DM Serif Display, serif' }}>Watch out for</h3>
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

        {/* Key Metrics */}
        <div className="card p-6 mb-8">
          <h3 className="font-medium mb-6" style={{ fontFamily: 'DM Serif Display, serif' }}>Key numbers</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center p-4 rounded-xl bg-neutral-50">
              <div className="text-3xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif', color: input.credit_score >= 700 ? '#7c9a82' : input.credit_score < 600 ? '#c4704f' : '#1a1a18' }}>
                {input.credit_score}
              </div>
              <p className="text-xs text-neutral-500">Credit Score</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-neutral-50">
              <div className="text-3xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif', color: rentToIncome <= 30 ? '#7c9a82' : rentToIncome > 40 ? '#c4704f' : '#1a1a18' }}>
                {rentToIncome}%
              </div>
              <p className="text-xs text-neutral-500">Rent/Income</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-neutral-50">
              <div className="text-3xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                {input.rental_history_years}y
              </div>
              <p className="text-xs text-neutral-500">Renting History</p>
            </div>
            <div className="text-center p-4 rounded-xl bg-neutral-50">
              <div className="text-3xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif', color: input.previous_evictions > 0 ? '#c4704f' : '#7c9a82' }}>
                {input.previous_evictions}
              </div>
              <p className="text-xs text-neutral-500">Evictions</p>
            </div>
          </div>
        </div>

        {/* Detailed Breakdown */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="card p-6">
            <h3 className="text-xs uppercase tracking-wide text-neutral-400 mb-4">Financial Details</h3>
            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Monthly income</span>
                <span className="font-medium">₹{input.monthly_income.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Monthly rent</span>
                <span className="font-medium">₹{input.monthly_rent.toLocaleString()}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Credit score</span>
                <span className="font-medium">{input.credit_score}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-neutral-600">Income verified</span>
                <span className={input.income_verified ? 'text-emerald-600 font-medium' : 'text-neutral-400'}>
                  {input.income_verified ? 'Yes' : 'No'}
                </span>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-xs uppercase tracking-wide text-neutral-400 mb-4">Background</h3>
            <div className="space-y-4">
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Years renting</span>
                <span className="font-medium">{input.rental_history_years}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Payment history</span>
                <span className="font-medium">{input.on_time_payments_percent}% on-time</span>
              </div>
              <div className="flex justify-between py-2 border-b border-neutral-100">
                <span className="text-neutral-600">Employment</span>
                <span className="font-medium capitalize">{input.employment_status.replace('-', ' ')}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-neutral-600">Employment verified</span>
                <span className={input.employment_verified ? 'text-emerald-600 font-medium' : 'text-neutral-400'}>
                  {input.employment_verified ? 'Yes' : 'No'}
                </span>
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
              <h3 className="font-medium text-neutral-900 mb-1">Pro tip</h3>
              <p className="text-sm text-neutral-600">
                {result.risk_category === 'LOW'
                  ? "This looks like a solid applicant. Consider locking in a longer lease term for stability."
                  : result.risk_category === 'MEDIUM'
                  ? "Request additional references or a larger security deposit to mitigate risk."
                  : "If you still want to proceed, consider a month-to-month lease with strict payment terms."}
              </p>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-2xl bg-white border border-neutral-100">
          <div className="text-center sm:text-left">
            <p className="font-medium text-neutral-900">What's next?</p>
            <p className="text-sm text-neutral-500">Score another applicant or review past assessments</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/score')}
              className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors px-4 py-2"
            >
              Score another
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-primary"
            >
              View all results
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
