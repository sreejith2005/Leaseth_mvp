import { clsx } from 'clsx'
import { RiskCategory, Recommendation } from '../../types'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export default function Badge({
  children,
  variant = 'default',
  size = 'md',
  className,
}: BadgeProps) {
  const variants = {
    default: 'bg-neutral-100 text-neutral-600',
    success: 'bg-emerald-100 text-emerald-700',
    warning: 'bg-amber-100 text-amber-700',
    danger: 'bg-red-100 text-red-700',
  }

  const sizes = {
    sm: 'px-2.5 py-1 text-xs',
    md: 'px-3 py-1.5 text-xs',
    lg: 'px-4 py-2 text-sm',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full',
        variants[variant],
        sizes[size],
        className
      )}
    >
      {children}
    </span>
  )
}

function getBaseRecommendation(recommendation: string): 'APPROVE' | 'MANUAL_REVIEW' | 'REJECT' {
  if (recommendation.startsWith('MANUAL_REVIEW')) return 'MANUAL_REVIEW'
  if (recommendation === 'APPROVE') return 'APPROVE'
  if (recommendation === 'REJECT') return 'REJECT'
  return 'MANUAL_REVIEW'
}

export function RiskBadge({ category, size = 'md' }: { category: RiskCategory; size?: 'sm' | 'md' | 'lg' }) {
  const variantMap: Record<RiskCategory, 'success' | 'warning' | 'danger'> = {
    LOW: 'success',
    MEDIUM: 'warning',
    HIGH: 'danger',
  }

  const labelMap: Record<RiskCategory, string> = {
    LOW: 'Low risk',
    MEDIUM: 'Medium risk',
    HIGH: 'High risk',
  }

  return (
    <Badge variant={variantMap[category]} size={size}>
      {labelMap[category]}
    </Badge>
  )
}

export function RecommendationBadge({ recommendation, size = 'md' }: { recommendation: Recommendation; size?: 'sm' | 'md' | 'lg' }) {
  const baseRec = getBaseRecommendation(recommendation)

  const variantMap: Record<string, 'success' | 'warning' | 'danger'> = {
    APPROVE: 'success',
    MANUAL_REVIEW: 'warning',
    REJECT: 'danger',
  }

  const labelMap: Record<string, string> = {
    APPROVE: 'Approve',
    MANUAL_REVIEW: 'Review',
    REJECT: 'Reject',
  }

  return (
    <Badge variant={variantMap[baseRec]} size={size}>
      {labelMap[baseRec]}
    </Badge>
  )
}
