import { ReactNode } from 'react'
import { LucideIcon, FileQuestion, Search, Users } from 'lucide-react'
import Button from './ui/Button'

interface EmptyStateProps {
  icon?: LucideIcon
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
  children?: ReactNode
}

export default function EmptyState({
  icon: Icon = FileQuestion,
  title,
  description,
  action,
  children,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mb-6">
        <Icon className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-xl font-semibold text-slate-900 mb-2">{title}</h3>
      {description && (
        <p className="text-slate-500 max-w-md mb-6">{description}</p>
      )}
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
      {children}
    </div>
  )
}

export function NoSearchResults({ onClear }: { onClear: () => void }) {
  return (
    <EmptyState
      icon={Search}
      title="No results found"
      description="We couldn't find any applicants matching your search criteria."
      action={{
        label: 'Clear Search',
        onClick: onClear,
      }}
    />
  )
}

export function NoApplicants({ onAdd }: { onAdd: () => void }) {
  return (
    <EmptyState
      icon={Users}
      title="No applicants yet"
      description="Start by scoring your first tenant applicant."
      action={{
        label: 'Score Applicant',
        onClick: onAdd,
      }}
    />
  )
}
