import { clsx } from 'clsx'
import { RiskCategory, OfferStatus, ReliabilityCategory } from '../../types'

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

export function OfferStatusBadge({ status, size = 'md' }: { status: OfferStatus; size?: 'sm' | 'md' | 'lg' }) {
  const variantMap: Record<OfferStatus, 'success' | 'danger'> = {
    OFFERED: 'success',
    NO_OFFER: 'danger',
  }

  const labelMap: Record<OfferStatus, string> = {
    OFFERED: 'Offer available',
    NO_OFFER: 'No offer',
  }

  return (
    <Badge variant={variantMap[status]} size={size}>
      {labelMap[status]}
    </Badge>
  )
}

export function ReliabilityBadge({ category, size = 'md' }: { category: ReliabilityCategory; size?: 'sm' | 'md' | 'lg' }) {
  const variantMap: Record<ReliabilityCategory, 'success' | 'warning' | 'danger'> = {
    HIGH: 'success',
    MEDIUM: 'warning',
    LOW: 'danger',
  }

  const labelMap: Record<ReliabilityCategory, string> = {
    HIGH: 'High reliability',
    MEDIUM: 'Medium reliability',
    LOW: 'Low reliability',
  }

  return (
    <Badge variant={variantMap[category]} size={size}>
      {labelMap[category]}
    </Badge>
  )
}

/** @deprecated - kept for backward compat with old components */
export function RecommendationBadge({ recommendation, size = 'md' }: { recommendation: string; size?: 'sm' | 'md' | 'lg' }) {
  return (
    <Badge variant="default" size={size}>
      {recommendation}
    </Badge>
  )
}
