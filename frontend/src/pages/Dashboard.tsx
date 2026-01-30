import { useState, useMemo, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Plus, Search, RefreshCw, Users, TrendingUp, AlertTriangle, XCircle } from 'lucide-react'
import { RiskBadge, RecommendationBadge } from '../components/ui/Badge'
import { StoredApplicant, RiskCategory } from '../types'
import { fetchApplicants } from '../services/api'

interface DashboardProps {
  showToast: (message: string, type: 'success' | 'error' | 'info') => void
}

export default function Dashboard({ showToast }: DashboardProps) {
  const navigate = useNavigate()
  const [applicants, setApplicants] = useState<StoredApplicant[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [riskFilter, setRiskFilter] = useState<RiskCategory | ''>('')

  const loadApplicants = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await fetchApplicants()
      setApplicants(data)
      // No error even if empty - fetchApplicants now falls back to local storage
    } catch (err) {
      // This should rarely happen now since fetchApplicants handles errors
      const message = err instanceof Error ? err.message : 'Failed to load'
      setError(message)
      console.error('Dashboard load error:', err)
      // Don't show toast for expected offline behavior
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadApplicants()
  }, [])

  const filteredApplicants = useMemo(() => {
    return applicants.filter(applicant => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase()
        const matchesName = applicant.input.name?.toLowerCase().includes(query)
        const matchesId = applicant.id.toLowerCase().includes(query)
        if (!matchesName && !matchesId) return false
      }
      if (riskFilter && applicant.result.risk_category !== riskFilter) {
        return false
      }
      return true
    })
  }, [applicants, searchQuery, riskFilter])

  const stats = useMemo(() => {
    if (applicants.length === 0) return null
    const low = applicants.filter(a => a.result.risk_category === 'LOW').length
    const medium = applicants.filter(a => a.result.risk_category === 'MEDIUM').length
    const high = applicants.filter(a => a.result.risk_category === 'HIGH').length
    const avgScore = Math.round(applicants.reduce((sum, a) => sum + a.result.risk_score, 0) / applicants.length)
    return { low, medium, high, avgScore, total: applicants.length }
  }, [applicants])

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

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
        <header className="sticky top-0 z-40 backdrop-blur-md bg-[#faf8f5]/80 border-b border-neutral-200/50">
          <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-4">
            <Link to="/" className="text-neutral-400 hover:text-neutral-900 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <span className="text-sm text-neutral-400">Loading assessments...</span>
          </div>
        </header>
        <div className="flex items-center justify-center py-32">
          <div className="flex flex-col items-center gap-4">
            <div className="w-8 h-8 border-2 border-[#7c9a82] border-t-transparent rounded-full animate-spin" />
            <p className="text-neutral-500">Fetching your data...</p>
          </div>
        </div>
      </div>
    )
  }

  // Note: We no longer show error state since fetchApplicants falls back to local storage
  // Error state is kept only for unexpected failures
  if (error && applicants.length === 0 && !isLoading) {
    // Even with an error, just show empty state - we'll try local storage
    console.warn('Dashboard error state reached:', error)
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--color-cream)' }}>
      {/* Header */}
      <header className="sticky top-0 z-40 backdrop-blur-md bg-[#faf8f5]/80 border-b border-neutral-200/50">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2 text-neutral-500 hover:text-neutral-900 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm hidden sm:inline">Home</span>
            </Link>
            <div className="h-6 w-px bg-neutral-200" />
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-[#7c9a82] flex items-center justify-center">
                <span className="text-white text-xs">L</span>
              </div>
              <span className="text-sm font-medium">Dashboard</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadApplicants}
              className="p-2 rounded-lg text-neutral-400 hover:text-neutral-900 hover:bg-white/50 transition-all"
              title="Refresh"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/score')}
              className="btn-primary text-sm"
            >
              <Plus className="w-4 h-4 mr-1" />
              New
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Page title */}
        <div className="mb-8">
          <h1 className="text-2xl md:text-3xl mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
            Your assessments
          </h1>
          <p className="text-neutral-500">
            {applicants.length === 0
              ? "You haven't scored any tenants yet"
              : `${applicants.length} total assessment${applicants.length !== 1 ? 's' : ''}`}
          </p>
        </div>

        {/* Empty state */}
        {applicants.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-[#7c9a82]/10 flex items-center justify-center mx-auto mb-6">
              <Users className="w-8 h-8 text-[#7c9a82]" />
            </div>
            <h2 className="text-xl mb-2" style={{ fontFamily: 'DM Serif Display, serif' }}>
              No assessments yet
            </h2>
            <p className="text-neutral-500 mb-8 max-w-sm mx-auto">
              Score your first tenant to start building your assessment history.
              It only takes a minute.
            </p>
            <button
              onClick={() => navigate('/score')}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Score your first tenant
            </button>
          </div>
        ) : (
          <>
            {/* Stats */}
            {stats && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="card p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center">
                      <Users className="w-5 h-5 text-neutral-600" />
                    </div>
                  </div>
                  <p className="text-3xl font-light mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                    {stats.total}
                  </p>
                  <p className="text-xs text-neutral-500">Total assessed</p>
                </div>
                <div className="card p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-emerald-600" />
                    </div>
                  </div>
                  <p className="text-3xl font-light text-emerald-600 mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                    {stats.low}
                  </p>
                  <p className="text-xs text-neutral-500">Low risk</p>
                </div>
                <div className="card p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center">
                      <AlertTriangle className="w-5 h-5 text-amber-600" />
                    </div>
                  </div>
                  <p className="text-3xl font-light text-amber-600 mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                    {stats.medium}
                  </p>
                  <p className="text-xs text-neutral-500">Medium risk</p>
                </div>
                <div className="card p-5">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-10 h-10 rounded-xl bg-red-100 flex items-center justify-center">
                      <XCircle className="w-5 h-5 text-red-600" />
                    </div>
                  </div>
                  <p className="text-3xl font-light text-red-600 mb-1" style={{ fontFamily: 'DM Serif Display, serif' }}>
                    {stats.high}
                  </p>
                  <p className="text-xs text-neutral-500">High risk</p>
                </div>
              </div>
            )}

            {/* Filters */}
            <div className="card p-4 mb-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    type="text"
                    placeholder="Search by name..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-11 pr-4 py-2.5 border border-neutral-200 rounded-lg focus:outline-none focus:border-[#7c9a82] focus:ring-2 focus:ring-[#7c9a82]/10 transition-all placeholder:text-neutral-400"
                  />
                </div>
                <div className="flex gap-2">
                  {([
                    { value: '', label: 'All' },
                    { value: 'LOW', label: 'Low' },
                    { value: 'MEDIUM', label: 'Medium' },
                    { value: 'HIGH', label: 'High' },
                  ] as const).map((filter) => (
                    <button
                      key={filter.value || 'all'}
                      onClick={() => setRiskFilter(filter.value)}
                      className={`px-4 py-2 text-sm rounded-lg transition-all duration-200 ${
                        riskFilter === filter.value
                          ? 'bg-[#1a1a18] text-white'
                          : 'bg-neutral-100 text-neutral-600 hover:bg-neutral-200'
                      }`}
                    >
                      {filter.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* List */}
            <div className="card overflow-hidden">
              <div className="divide-y divide-neutral-100">
                {filteredApplicants.map((applicant, index) => (
                  <div
                    key={applicant.id}
                    className="flex items-center justify-between p-4 hover:bg-neutral-50/50 transition-colors cursor-pointer group"
                    onClick={() => showToast(`Selected: ${applicant.input.name}`, 'info')}
                    style={{ animationDelay: `${index * 50}ms` }}
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className="w-11 h-11 rounded-xl flex items-center justify-center text-sm font-medium text-white"
                        style={{
                          backgroundColor: applicant.result.risk_category === 'LOW'
                            ? '#7c9a82'
                            : applicant.result.risk_category === 'MEDIUM'
                            ? '#d4a574'
                            : '#c4704f'
                        }}
                      >
                        {(applicant.input.name || '?')[0].toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium text-neutral-900 group-hover:text-[#7c9a82] transition-colors">
                          {applicant.input.name || 'Unknown'}
                        </p>
                        <p className="text-sm text-neutral-400">
                          {applicant.input.location || 'No location'} • {applicant.input.property_type || 'Property'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right hidden sm:block">
                        <span className={`text-2xl font-light ${
                          applicant.result.risk_category === 'LOW' ? 'text-emerald-600' :
                          applicant.result.risk_category === 'MEDIUM' ? 'text-amber-600' : 'text-red-600'
                        }`} style={{ fontFamily: 'DM Serif Display, serif' }}>
                          {applicant.result.risk_score}
                        </span>
                      </div>
                      <div className="hidden md:flex items-center gap-2">
                        <RiskBadge category={applicant.result.risk_category} size="sm" />
                        <RecommendationBadge recommendation={applicant.result.recommendation} size="sm" />
                      </div>
                      <span className="text-sm text-neutral-400 w-20 text-right">
                        {formatDate(applicant.scored_at)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Empty filter state */}
            {filteredApplicants.length === 0 && (searchQuery || riskFilter) && (
              <div className="card p-12 text-center">
                <p className="text-neutral-500 mb-4">No results match your filters</p>
                <button
                  onClick={() => { setSearchQuery(''); setRiskFilter(''); }}
                  className="text-sm text-[#7c9a82] hover:underline transition-colors"
                >
                  Clear filters
                </button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
