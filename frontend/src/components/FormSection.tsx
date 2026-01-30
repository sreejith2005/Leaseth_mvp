import { ReactNode } from 'react'
import { clsx } from 'clsx'

interface FormSectionProps {
  title: string
  description?: string
  children: ReactNode
  className?: string
}

export default function FormSection({
  title,
  description,
  children,
  className,
}: FormSectionProps) {
  return (
    <div className={clsx('pb-8 border-b border-neutral-100 last:border-0 last:pb-0', className)}>
      <div className="mb-6">
        <h2 className="text-sm font-medium text-neutral-900">{title}</h2>
        {description && (
          <p className="text-xs text-neutral-400 mt-1">{description}</p>
        )}
      </div>
      <div className="space-y-6">{children}</div>
    </div>
  )
}

interface FormRowProps {
  children: ReactNode
  className?: string
}

export function FormRow({ children, className }: FormRowProps) {
  return (
    <div className={clsx('grid gap-6 md:grid-cols-2', className)}>
      {children}
    </div>
  )
}
