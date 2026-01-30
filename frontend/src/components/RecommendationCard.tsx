import { CheckCircle, AlertCircle, XCircle, Clock, LucideIcon } from 'lucide-react'
import { Recommendation, RiskCategory } from '../types'
import { RiskBadge, RecommendationBadge } from './ui/Badge'

interface RecommendationCardProps {
  recommendation: Recommendation
  category: RiskCategory
  confidence: number
  reasoning: string
  processingTime: number
}

// Get base recommendation type (handle "MANUAL_REVIEW (Lean Approve)" etc.)
function getBaseRecommendation(recommendation: string): 'APPROVE' | 'MANUAL_REVIEW' | 'REJECT' {
  if (recommendation.startsWith('MANUAL_REVIEW')) return 'MANUAL_REVIEW'
  if (recommendation === 'APPROVE') return 'APPROVE'
  if (recommendation === 'REJECT') return 'REJECT'
  return 'MANUAL_REVIEW' // Default fallback
}

export default function RecommendationCard({
  recommendation,
  category,
  confidence,
  reasoning,
  processingTime,
}: RecommendationCardProps) {
  const icons: Record<string, LucideIcon> = {
    APPROVE: CheckCircle,
    MANUAL_REVIEW: AlertCircle,
    REJECT: XCircle,
  }

  const colors: Record<string, string> = {
    APPROVE: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    MANUAL_REVIEW: 'bg-amber-50 border-amber-200 text-amber-700',
    REJECT: 'bg-rose-50 border-rose-200 text-rose-700',
  }

  const iconColors: Record<string, string> = {
    APPROVE: 'text-emerald-500',
    MANUAL_REVIEW: 'text-amber-500',
    REJECT: 'text-rose-500',
  }

  const baseRec = getBaseRecommendation(recommendation)
  const Icon = icons[baseRec]

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className={`p-6 border-b-2 ${colors[baseRec]}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-full flex items-center justify-center ${
              baseRec === 'APPROVE' ? 'bg-emerald-100' :
              baseRec === 'MANUAL_REVIEW' ? 'bg-amber-100' : 'bg-rose-100'
            }`}>
              <Icon className={`w-7 h-7 ${iconColors[baseRec]}`} />
            </div>
            <div>
              <p className="text-sm font-medium opacity-70">Recommendation</p>
              <p className="text-2xl font-bold capitalize">
                {recommendation.replace('_', ' ')}
              </p>
            </div>
          </div>
          <RecommendationBadge recommendation={recommendation} size="lg" />
        </div>
      </div>

      {/* Details */}
      <div className="p-6 space-y-6">
        {/* Badges */}
        <div className="flex flex-wrap gap-3">
          <RiskBadge category={category} size="lg" />
          <div className="flex items-center gap-2 px-4 py-1.5 bg-slate-100 rounded-full">
            <Clock className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-medium text-slate-700">
              {(processingTime / 1000).toFixed(2)}s
            </span>
          </div>
        </div>

        {/* Confidence */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-slate-700">Confidence Level</span>
            <span className="text-sm font-bold text-primary-500">{Math.round(confidence * 100)}%</span>
          </div>
          <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full transition-all duration-1000"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
        </div>

        {/* Reasoning */}
        <div>
          <h4 className="text-sm font-medium text-slate-700 mb-2">AI Analysis</h4>
          <div className="bg-slate-50 rounded-lg p-4">
            <p className="text-slate-600 leading-relaxed">{reasoning}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
