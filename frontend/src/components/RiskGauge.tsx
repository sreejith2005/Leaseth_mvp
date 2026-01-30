import { useEffect, useState } from 'react'
import { RiskCategory } from '../types'

interface RiskGaugeProps {
  score: number
  category: RiskCategory
  size?: 'sm' | 'md' | 'lg'
  animated?: boolean
}

export default function RiskGauge({
  score,
  category,
  size = 'md',
  animated = true,
}: RiskGaugeProps) {
  const [displayScore, setDisplayScore] = useState(animated ? 0 : score)

  useEffect(() => {
    if (!animated) {
      setDisplayScore(score)
      return
    }

    // Animate the score counting up
    const duration = 1500
    const steps = 60
    const increment = score / steps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= score) {
        setDisplayScore(score)
        clearInterval(timer)
      } else {
        setDisplayScore(Math.round(current))
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [score, animated])

  const sizes = {
    sm: { width: 120, strokeWidth: 8, fontSize: 'text-2xl' },
    md: { width: 180, strokeWidth: 12, fontSize: 'text-4xl' },
    lg: { width: 240, strokeWidth: 16, fontSize: 'text-5xl' },
  }

  const { width, strokeWidth, fontSize } = sizes[size]
  const radius = (width - strokeWidth) / 2
  const circumference = radius * Math.PI // Half circle
  const progress = (displayScore / 100) * circumference

  const colors = {
    LOW: { stroke: '#10b981', bg: '#d1fae5', text: 'text-emerald-500' },
    MEDIUM: { stroke: '#f59e0b', bg: '#fef3c7', text: 'text-amber-500' },
    HIGH: { stroke: '#f43f5e', bg: '#ffe4e6', text: 'text-rose-500' },
  }

  const { stroke, bg, text } = colors[category]

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width, height: width / 2 + 20 }}>
        <svg
          width={width}
          height={width / 2 + 20}
          className="transform"
        >
          {/* Background arc */}
          <path
            d={`M ${strokeWidth / 2}, ${width / 2}
                A ${radius}, ${radius} 0 0 1 ${width - strokeWidth / 2}, ${width / 2}`}
            fill="none"
            stroke={bg}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
          />
          {/* Progress arc */}
          <path
            d={`M ${strokeWidth / 2}, ${width / 2}
                A ${radius}, ${radius} 0 0 1 ${width - strokeWidth / 2}, ${width / 2}`}
            fill="none"
            stroke={stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference - progress}
            className="transition-all duration-1000 ease-out"
          />
        </svg>

        {/* Score display */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-end pb-2"
        >
          <span className={`${fontSize} font-bold ${text}`}>
            {displayScore}
          </span>
          <span className="text-sm text-slate-500">Risk Score</span>
        </div>
      </div>

      {/* Scale labels */}
      <div className="flex justify-between w-full px-2 -mt-1">
        <span className="text-xs text-emerald-500 font-medium">0</span>
        <span className="text-xs text-slate-400">50</span>
        <span className="text-xs text-rose-500 font-medium">100</span>
      </div>
    </div>
  )
}
