import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { StoredApplicant } from '../types'

interface ChartProps {
  applicants: StoredApplicant[]
}

const RISK_COLORS = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#f43f5e',
}

const RECOMMENDATION_COLORS = {
  APPROVE: '#10b981',
  MANUAL_REVIEW: '#f59e0b',
  REJECT: '#f43f5e',
}

export function RiskPieChart({ applicants }: ChartProps) {
  const data = [
    { name: 'Low Risk', value: applicants.filter(a => a.result.risk_category === 'LOW').length, color: RISK_COLORS.LOW },
    { name: 'Medium Risk', value: applicants.filter(a => a.result.risk_category === 'MEDIUM').length, color: RISK_COLORS.MEDIUM },
    { name: 'High Risk', value: applicants.filter(a => a.result.risk_category === 'HIGH').length, color: RISK_COLORS.HIGH },
  ].filter(d => d.value > 0)

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400">
        No data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={4}
          dataKey="value"
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number) => [`${value} applicants`, 'Count']}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

export function RecommendationBarChart({ applicants }: ChartProps) {
  const data = [
    { name: 'Approve', count: applicants.filter(a => a.result.recommendation === 'APPROVE').length, fill: RECOMMENDATION_COLORS.APPROVE },
    { name: 'Review', count: applicants.filter(a => a.result.recommendation === 'MANUAL_REVIEW').length, fill: RECOMMENDATION_COLORS.MANUAL_REVIEW },
    { name: 'Reject', count: applicants.filter(a => a.result.recommendation === 'REJECT').length, fill: RECOMMENDATION_COLORS.REJECT },
  ]

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" tick={{ fill: '#64748b' }} />
        <YAxis allowDecimals={false} tick={{ fill: '#64748b' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
          }}
          formatter={(value: number) => [`${value} applicants`, 'Count']}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export function ScoreDistributionChart({ applicants }: ChartProps) {
  // Group scores into ranges
  const ranges = [
    { range: '0-20', min: 0, max: 20, color: '#10b981' },
    { range: '21-40', min: 21, max: 40, color: '#22c55e' },
    { range: '41-60', min: 41, max: 60, color: '#f59e0b' },
    { range: '61-80', min: 61, max: 80, color: '#f97316' },
    { range: '81-100', min: 81, max: 100, color: '#f43f5e' },
  ]

  const data = ranges.map(r => ({
    range: r.range,
    count: applicants.filter(a => a.result.risk_score >= r.min && a.result.risk_score <= r.max).length,
    fill: r.color,
  }))

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="range" tick={{ fill: '#64748b' }} />
        <YAxis allowDecimals={false} tick={{ fill: '#64748b' }} />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e2e8f0',
            borderRadius: '8px',
          }}
          formatter={(value: number) => [`${value} applicants`, 'Count']}
        />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
