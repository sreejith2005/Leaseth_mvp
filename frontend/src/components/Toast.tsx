import { useEffect } from 'react'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { clsx } from 'clsx'

interface ToastProps {
  message: string
  type: 'success' | 'error' | 'info'
  onClose: () => void
  duration?: number
}

export default function Toast({ message, type, onClose, duration = 4000 }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(onClose, duration)
    return () => clearTimeout(timer)
  }, [duration, onClose])

  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    info: Info,
  }

  const styles = {
    success: 'bg-white border-emerald-200',
    error: 'bg-white border-red-200',
    info: 'bg-white border-[#7c9a82]/30',
  }

  const iconStyles = {
    success: 'text-emerald-500 bg-emerald-50',
    error: 'text-red-500 bg-red-50',
    info: 'text-[#7c9a82] bg-[#7c9a82]/10',
  }

  const Icon = icons[type]

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-slide-up">
      <div
        className={clsx(
          'flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg max-w-md',
          styles[type]
        )}
        style={{
          animation: 'slideUp 0.3s ease-out',
        }}
      >
        <div className={clsx('w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0', iconStyles[type])}>
          <Icon className="w-4 h-4" />
        </div>
        <p className="text-sm font-medium text-neutral-800 flex-1">{message}</p>
        <button
          onClick={onClose}
          className="p-1.5 hover:bg-neutral-100 rounded-lg transition-colors text-neutral-400 hover:text-neutral-600"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      <style>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  )
}
