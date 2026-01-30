import { TrendingUp, Users, Target, AlertTriangle } from 'lucide-react'
import { StoredApplicant } from '../types'

interface StatsPanelProps {
  applicants: StoredApplicant[]
}

export default function StatsPanel({ applicants }: StatsPanelProps) {
  const totalApplications = applicants.length
  const avgRiskScore = totalApplications > 0
    ? Math.round(applicants.reduce((sum, a) => sum + a.result.risk_score, 0) / totalApplications)
    : 0

  const approvedCount = applicants.filter(a => a.result.recommendation === 'APPROVE').length
  const reviewCount = applicants.filter(a => a.result.recommendation === 'MANUAL_REVIEW').length

  const approvalRate = totalApplications > 0
    ? Math.round((approvedCount / totalApplications) * 100)
    : 0

  const stats = [
    {
      label: 'Total Applications',
      value: totalApplications,
      icon: Users,
      color: 'bg-primary-100 text-primary-500',
      trend: null,
    },
    {
      label: 'Avg. Risk Score',
      value: avgRiskScore,
      icon: Target,
      color: avgRiskScore <= 40 ? 'bg-emerald-100 text-emerald-500' :
             avgRiskScore <= 60 ? 'bg-amber-100 text-amber-500' : 'bg-rose-100 text-rose-500',
      trend: null,
    },
    {
      label: 'Approval Rate',
      value: `${approvalRate}%`,
      icon: TrendingUp,
      color: 'bg-emerald-100 text-emerald-500',
      trend: null,
    },
    {
      label: 'Pending Review',
      value: reviewCount,
      icon: AlertTriangle,
      color: 'bg-amber-100 text-amber-500',
      trend: null,
    },
  ]

  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat) => (
        <div
          key={stat.label}
          className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-slate-500 mb-1">{stat.label}</p>
              <p className="text-3xl font-bold text-slate-900">{stat.value}</p>
            </div>
            <div className={`w-12 h-12 rounded-lg ${stat.color} flex items-center justify-center`}>
              <stat.icon className="w-6 h-6" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

interface CategoryBreakdownProps {
  applicants: StoredApplicant[]
}

export function CategoryBreakdown({ applicants }: CategoryBreakdownProps) {
  const total = applicants.length
  const lowCount = applicants.filter(a => a.result.risk_category === 'LOW').length
  const mediumCount = applicants.filter(a => a.result.risk_category === 'MEDIUM').length
  const highCount = applicants.filter(a => a.result.risk_category === 'HIGH').length

  const categories = [
    { label: 'Low Risk', count: lowCount, percentage: total ? Math.round((lowCount / total) * 100) : 0, color: 'bg-emerald-500' },
    { label: 'Medium Risk', count: mediumCount, percentage: total ? Math.round((mediumCount / total) * 100) : 0, color: 'bg-amber-500' },
    { label: 'High Risk', count: highCount, percentage: total ? Math.round((highCount / total) * 100) : 0, color: 'bg-rose-500' },
  ]

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Risk Distribution</h3>
      <div className="space-y-4">
        {categories.map((cat) => (
          <div key={cat.label}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-slate-600">{cat.label}</span>
              <span className="text-sm font-semibold text-slate-900">
                {cat.count} ({cat.percentage}%)
              </span>
            </div>
            <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${cat.color} rounded-full transition-all duration-500`}
                style={{ width: `${cat.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

interface RecommendationBreakdownProps {
  applicants: StoredApplicant[]
}

export function RecommendationBreakdown({ applicants }: RecommendationBreakdownProps) {
  const total = applicants.length
  const approveCount = applicants.filter(a => a.result.recommendation === 'APPROVE').length
  const reviewCount = applicants.filter(a => a.result.recommendation === 'MANUAL_REVIEW').length
  const rejectCount = applicants.filter(a => a.result.recommendation === 'REJECT').length

  const recommendations = [
    { label: 'Approved', count: approveCount, color: 'bg-emerald-500 text-white' },
    { label: 'Manual Review', count: reviewCount, color: 'bg-amber-500 text-white' },
    { label: 'Rejected', count: rejectCount, color: 'bg-rose-500 text-white' },
  ]

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h3 className="text-lg font-semibold text-slate-900 mb-4">Recommendations</h3>
      <div className="flex gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.label}
            className={`flex-1 ${rec.color} rounded-lg p-4 text-center`}
          >
            <p className="text-3xl font-bold">{rec.count}</p>
            <p className="text-sm opacity-90">{rec.label}</p>
          </div>
        ))}
      </div>
      {total === 0 && (
        <p className="text-center text-slate-500 mt-4">No data yet</p>
      )}
    </div>
  )
}
