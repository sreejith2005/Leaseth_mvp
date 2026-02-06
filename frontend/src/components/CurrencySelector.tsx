import { useState, useRef, useEffect } from 'react'
import { ChevronDown } from 'lucide-react'
import { useCurrency } from '../contexts/CurrencyContext'
import { CURRENCY_LIST } from '../utils/currency'

export default function CurrencySelector() {
  const { currencyCode, currency, setCurrency } = useCurrency()
  const [isOpen, setIsOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm text-neutral-600 hover:bg-neutral-100 transition-colors border border-neutral-200"
        aria-label="Select currency"
      >
        <span>{currency.flag}</span>
        <span className="font-medium">{currencyCode}</span>
        <ChevronDown className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-64 max-h-80 overflow-y-auto bg-white rounded-xl shadow-lg border border-neutral-200 z-50 py-1">
          {CURRENCY_LIST.map((c) => (
            <button
              key={c.code}
              type="button"
              onClick={() => {
                setCurrency(c.code)
                setIsOpen(false)
              }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                c.code === currencyCode
                  ? 'bg-[#7c9a82]/10 text-[#7c9a82] font-medium'
                  : 'text-neutral-700 hover:bg-neutral-50'
              }`}
            >
              <span className="text-lg">{c.flag}</span>
              <span className="font-medium">{c.code}</span>
              <span className="text-neutral-400 text-xs ml-auto">{c.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
