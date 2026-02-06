// ============================================================
// Leaseth - Global Multi-Currency Support
// ============================================================

export interface CurrencyConfig {
  code: string       // ISO 4217 code (e.g. "USD")
  symbol: string     // Symbol (e.g. "$")
  name: string       // Display name (e.g. "US Dollar")
  locale: string     // BCP 47 locale for formatting (e.g. "en-US")
  flag: string       // Flag emoji
}

/**
 * Curated list of ~18 supported currencies covering
 * North America, Europe, Middle East, Asia, Africa, Oceania.
 */
export const SUPPORTED_CURRENCIES: Record<string, CurrencyConfig> = {
  USD: { code: 'USD', symbol: '$',   name: 'US Dollar',           locale: 'en-US',  flag: '🇺🇸' },
  EUR: { code: 'EUR', symbol: '€',   name: 'Euro',                locale: 'de-DE',  flag: '🇪🇺' },
  GBP: { code: 'GBP', symbol: '£',   name: 'British Pound',       locale: 'en-GB',  flag: '🇬🇧' },
  AED: { code: 'AED', symbol: 'د.إ', name: 'UAE Dirham',          locale: 'ar-AE',  flag: '🇦🇪' },
  SAR: { code: 'SAR', symbol: '﷼',   name: 'Saudi Riyal',         locale: 'ar-SA',  flag: '🇸🇦' },
  CHF: { code: 'CHF', symbol: 'Fr',  name: 'Swiss Franc',         locale: 'de-CH',  flag: '🇨🇭' },
  CAD: { code: 'CAD', symbol: 'C$',  name: 'Canadian Dollar',     locale: 'en-CA',  flag: '🇨🇦' },
  AUD: { code: 'AUD', symbol: 'A$',  name: 'Australian Dollar',   locale: 'en-AU',  flag: '🇦🇺' },
  INR: { code: 'INR', symbol: '₹',   name: 'Indian Rupee',        locale: 'en-IN',  flag: '🇮🇳' },
  JPY: { code: 'JPY', symbol: '¥',   name: 'Japanese Yen',        locale: 'ja-JP',  flag: '🇯🇵' },
  SGD: { code: 'SGD', symbol: 'S$',  name: 'Singapore Dollar',    locale: 'en-SG',  flag: '🇸🇬' },
  SEK: { code: 'SEK', symbol: 'kr',  name: 'Swedish Krona',       locale: 'sv-SE',  flag: '🇸🇪' },
  NOK: { code: 'NOK', symbol: 'kr',  name: 'Norwegian Krone',     locale: 'nb-NO',  flag: '🇳🇴' },
  DKK: { code: 'DKK', symbol: 'kr',  name: 'Danish Krone',        locale: 'da-DK',  flag: '🇩🇰' },
  PLN: { code: 'PLN', symbol: 'zł',  name: 'Polish Złoty',        locale: 'pl-PL',  flag: '🇵🇱' },
  BRL: { code: 'BRL', symbol: 'R$',  name: 'Brazilian Real',      locale: 'pt-BR',  flag: '🇧🇷' },
  MXN: { code: 'MXN', symbol: 'Mex$', name: 'Mexican Peso',      locale: 'es-MX',  flag: '🇲🇽' },
  ZAR: { code: 'ZAR', symbol: 'R',   name: 'South African Rand',  locale: 'en-ZA',  flag: '🇿🇦' },
}

/** Ordered list for dropdown rendering */
export const CURRENCY_LIST: CurrencyConfig[] = Object.values(SUPPORTED_CURRENCIES)

/**
 * Detect the best default currency from the browser locale.
 * Falls back to USD if no match found.
 */
export function detectCurrencyFromLocale(): string {
  try {
    const lang = navigator.language || navigator.languages?.[0] || 'en-US'

    // Map common browser locale prefixes → currency codes
    const localeMap: Record<string, string> = {
      'en-US': 'USD',
      'en-GB': 'GBP',
      'en-AU': 'AUD',
      'en-CA': 'CAD',
      'en-IN': 'INR',
      'en-SG': 'SGD',
      'en-ZA': 'ZAR',
      'de-DE': 'EUR',
      'de-AT': 'EUR',
      'de-CH': 'CHF',
      'fr-FR': 'EUR',
      'fr-CH': 'CHF',
      'fr-CA': 'CAD',
      'it-IT': 'EUR',
      'it-CH': 'CHF',
      'es-ES': 'EUR',
      'es-MX': 'MXN',
      'pt-BR': 'BRL',
      'pt-PT': 'EUR',
      'nl-NL': 'EUR',
      'nl-BE': 'EUR',
      'sv-SE': 'SEK',
      'nb-NO': 'NOK',
      'da-DK': 'DKK',
      'pl-PL': 'PLN',
      'ja-JP': 'JPY',
      'ar-AE': 'AED',
      'ar-SA': 'SAR',
      'hi-IN': 'INR',
    }

    // Try exact match first
    if (localeMap[lang]) return localeMap[lang]

    // Try language-only fallback
    const langPrefix = lang.split('-')[0]
    const fallbackMap: Record<string, string> = {
      en: 'USD',
      de: 'EUR',
      fr: 'EUR',
      it: 'EUR',
      es: 'EUR',
      pt: 'EUR',
      nl: 'EUR',
      sv: 'SEK',
      nb: 'NOK',
      no: 'NOK',
      da: 'DKK',
      pl: 'PLN',
      ja: 'JPY',
      ar: 'AED',
      hi: 'INR',
    }

    return fallbackMap[langPrefix] || 'USD'
  } catch {
    return 'USD'
  }
}

/**
 * Format a number as currency using the Intl.NumberFormat API.
 * Produces locale-correct grouping separators and currency symbol placement.
 */
export function formatAmount(amount: number, currencyCode: string): string {
  const config = SUPPORTED_CURRENCIES[currencyCode] || SUPPORTED_CURRENCIES.USD
  try {
    return new Intl.NumberFormat(config.locale, {
      style: 'currency',
      currency: config.code,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  } catch {
    // Fallback: simple symbol + comma formatting
    return `${config.symbol}${amount.toLocaleString()}`
  }
}

/**
 * Get just the currency symbol for use as input prefix.
 */
export function getCurrencySymbol(currencyCode: string): string {
  return SUPPORTED_CURRENCIES[currencyCode]?.symbol || '$'
}
