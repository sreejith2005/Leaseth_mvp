import { clsx } from 'clsx'

interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export default function Skeleton({
  className,
  variant = 'text',
  width,
  height,
}: SkeletonProps) {
  const baseStyles = 'animate-pulse bg-slate-200'

  const variants = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-lg',
  }

  const style: React.CSSProperties = {
    width: width,
    height: height,
  }

  return (
    <div
      className={clsx(baseStyles, variants[variant], className)}
      style={style}
    />
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 space-y-4">
      <Skeleton variant="text" className="w-3/4 h-6" />
      <Skeleton variant="text" className="w-full h-4" />
      <Skeleton variant="text" className="w-full h-4" />
      <Skeleton variant="text" className="w-2/3 h-4" />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      <div className="p-4 border-b border-slate-200">
        <Skeleton variant="text" className="w-48 h-6" />
      </div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="p-4 flex items-center gap-4">
            <Skeleton variant="circular" width={40} height={40} />
            <div className="flex-1 space-y-2">
              <Skeleton variant="text" className="w-1/4 h-4" />
              <Skeleton variant="text" className="w-1/2 h-3" />
            </div>
            <Skeleton variant="rectangular" width={80} height={24} />
          </div>
        ))}
      </div>
    </div>
  )
}
