import { createContext, useContext, useCallback, ReactNode } from 'react'
import { useLocalStorage } from '../hooks/useLocalStorage'
import {
  CurrencyConfig,
  SUPPORTED_CURRENCIES,
  detectCurrencyFromLocale,
  formatAmount,
  getCurrencySymbol,
} from '../utils/currency'

interface CurrencyContextValue {
  /** Current active currency code (e.g. "USD") */
  currencyCode: string
  /** Full config for the active currency */
  currency: CurrencyConfig
  /** Change the active currency */
  setCurrency: (code: string) => void
  /** Format a number as currency (e.g. "$12,500") */
  formatCurrency: (amount: number) => string
  /** Get just the symbol (e.g. "$") for input prefixes */
  symbol: string
}

const CurrencyContext = createContext<CurrencyContextValue | null>(null)

interface CurrencyProviderProps {
  children: ReactNode
}

export function CurrencyProvider({ children }: CurrencyProviderProps) {
  const detectedDefault = detectCurrencyFromLocale()
  const [currencyCode, setCurrencyCode] = useLocalStorage<string>('leaseth_currency', detectedDefault)

  const currency = SUPPORTED_CURRENCIES[currencyCode] || SUPPORTED_CURRENCIES.USD

  const handleSetCurrency = useCallback((code: string) => {
    if (SUPPORTED_CURRENCIES[code]) {
      setCurrencyCode(code)
    }
  }, [setCurrencyCode])

  const format = useCallback((amount: number) => {
    return formatAmount(amount, currencyCode)
  }, [currencyCode])

  const symbol = getCurrencySymbol(currencyCode)

  return (
    <CurrencyContext.Provider
      value={{
        currencyCode,
        currency,
        setCurrency: handleSetCurrency,
        formatCurrency: format,
        symbol,
      }}
    >
      {children}
    </CurrencyContext.Provider>
  )
}

/**
 * Hook to access currency context.
 * Must be used inside <CurrencyProvider>.
 */
export function useCurrency(): CurrencyContextValue {
  const context = useContext(CurrencyContext)
  if (!context) {
    throw new Error('useCurrency must be used within a CurrencyProvider')
  }
  return context
}

export default CurrencyContext
