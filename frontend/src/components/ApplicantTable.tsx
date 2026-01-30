import { useState } from 'react'
import { StoredApplicant } from '../types'
import { RiskBadge, RecommendationBadge } from './ui/Badge'
import { ChevronDown, ChevronUp, User } from 'lucide-react'

interface ApplicantTableProps {
  applicants: StoredApplicant[]
  onSelect?: (applicant: StoredApplicant) => void
}

type SortField = 'name' | 'risk_score' | 'scored_at'
type SortDirection = 'asc' | 'desc'

export default function ApplicantTable({ applicants, onSelect }: ApplicantTableProps) {
  const [sortField, setSortField] = useState<SortField>('scored_at')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  const sortedApplicants = [...applicants].sort((a, b) => {
    let comparison = 0

    switch (sortField) {
      case 'name':
        comparison = (a.input.name || '').localeCompare(b.input.name || '')
        break
      case 'risk_score':
        comparison = a.result.risk_score - b.result.risk_score
        break
      case 'scored_at':
        comparison = new Date(a.scored_at).getTime() - new Date(b.scored_at).getTime()
        break
    }

    return sortDirection === 'asc' ? comparison : -comparison
  })

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Desktop Table */}
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50 border-b border-slate-200">
            <tr>
              <th
                className="px-6 py-4 text-left text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center gap-2">
                  Applicant
                  <SortIcon field="name" />
                </div>
              </th>
              <th
                className="px-6 py-4 text-left text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100"
                onClick={() => handleSort('risk_score')}
              >
                <div className="flex items-center gap-2">
                  Risk Score
                  <SortIcon field="risk_score" />
                </div>
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                Category
              </th>
              <th className="px-6 py-4 text-left text-sm font-semibold text-slate-700">
                Recommendation
              </th>
              <th
                className="px-6 py-4 text-left text-sm font-semibold text-slate-700 cursor-pointer hover:bg-slate-100"
                onClick={() => handleSort('scored_at')}
              >
                <div className="flex items-center gap-2">
                  Date
                  <SortIcon field="scored_at" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sortedApplicants.map((applicant) => (
              <tr
                key={applicant.id}
                className="hover:bg-slate-50 cursor-pointer transition-colors"
                onClick={() => onSelect?.(applicant)}
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                      <User className="w-5 h-5 text-primary-500" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-900">{applicant.input.name}</p>
                      <p className="text-sm text-slate-500">{applicant.input.location}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${
                      applicant.result.risk_category === 'LOW' ? 'bg-emerald-500' :
                      applicant.result.risk_category === 'MEDIUM' ? 'bg-amber-500' : 'bg-rose-500'
                    }`} />
                    <span className="font-semibold text-slate-900">
                      {applicant.result.risk_score}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <RiskBadge category={applicant.result.risk_category} size="sm" />
                </td>
                <td className="px-6 py-4">
                  <RecommendationBadge recommendation={applicant.result.recommendation} size="sm" />
                </td>
                <td className="px-6 py-4 text-sm text-slate-500">
                  {formatDate(applicant.scored_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Cards */}
      <div className="md:hidden divide-y divide-slate-100">
        {sortedApplicants.map((applicant) => (
          <div
            key={applicant.id}
            className="p-4 hover:bg-slate-50 cursor-pointer"
            onClick={() => onSelect?.(applicant)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <User className="w-5 h-5 text-primary-500" />
                </div>
                <div>
                  <p className="font-medium text-slate-900">{applicant.input.name}</p>
                  <p className="text-sm text-slate-500">{applicant.input.location}</p>
                </div>
              </div>
              <span className="text-sm text-slate-500">{formatDate(applicant.scored_at)}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-semibold text-slate-900">Score: {applicant.result.risk_score}</span>
              <RiskBadge category={applicant.result.risk_category} size="sm" />
              <RecommendationBadge recommendation={applicant.result.recommendation} size="sm" />
            </div>
          </div>
        ))}
      </div>

      {applicants.length === 0 && (
        <div className="p-12 text-center text-slate-500">
          <p>No applicants found</p>
        </div>
      )}
    </div>
  )
}
