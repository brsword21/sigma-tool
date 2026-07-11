import type { Listing, Recommendation, RunStatus } from '../api/types'

export const terminalStatus = (status: RunStatus) =>
  status === 'completed' || status === 'partial' || status === 'failed'

export const money = (value: string | number, currency = 'PLN') => {
  const amount = typeof value === 'number' ? value : Number(value)
  if (!Number.isFinite(amount)) return 'Brak ceny'
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount)
}

export const dateTime = (value?: string | null) => {
  if (!value) return 'Brak daty'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return 'Brak daty'
  return new Intl.DateTimeFormat('pl-PL', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(parsed)
}

export const fieldLabel = (value: unknown) =>
  value === null || value === undefined || value === 'unknown' || value === ''
    ? 'Brak danych'
    : String(value)

export const scoreLabel = (value: unknown) => {
  const score = Number(value)
  if (!Number.isFinite(score)) return 'Brak danych'
  if (score >= 75) return 'Mocne'
  if (score >= 50) return 'Dobre'
  return 'Ostrożnie'
}

export const listingFor = (recommendation: Recommendation): Listing | undefined =>
  recommendation.listings ?? recommendation.listing

export const sourceName = (recommendation: Recommendation) =>
  listingFor(recommendation)?.source?.replaceAll('_', ' ') ?? 'Nieznane źródło'

export const clampScore = (value: unknown) => {
  const score = Number(value)
  return Number.isFinite(score) ? Math.max(0, Math.min(100, Math.round(score))) : 0
}

export const formatMoney = money

export const formatRetrievedAt = dateTime

export const formatGap = (value: string) => value.replaceAll('_', ' ')

const BATTERY_PATTERN =
  /(?:bat\p{L}*|kondycj\p{L}*|zdrowi\p{L}*|health)\W{0,4}(\d{2,3})\s*%|(\d{2,3})\s*%\s*(?:bat\p{L}*|kondycj\p{L}*|zdrowi\p{L}*|health)/iu

export const batteryHealth = (listing?: Listing): number | null => {
  const match = listing?.title.match(BATTERY_PATTERN)
  if (!match) return null
  const value = Number(match[1] ?? match[2])
  return value >= 40 && value <= 100 ? value : null
}

export const capacityLabel = (listing?: Listing): string | null => {
  const match = listing?.title.match(/(\d{2,4})\s*(GB|TB)\b/i)
  return match ? `${match[1]} ${match[2].toUpperCase()}` : null
}

export const savingsVsNew = (price: string | number, benchmark?: string | number | null): string | null => {
  const offer = Number(price)
  const reference = Number(benchmark)
  if (!Number.isFinite(offer) || !Number.isFinite(reference) || offer <= 0 || reference <= 0) return null
  const delta = Math.round((1 - offer / reference) * 100)
  return delta >= 5 ? `${delta}% taniej niż nowy` : null
}

const gapNames: Record<string, string> = {
  warranty: 'gwarancja',
  returns: 'zwroty',
  seller_signals: 'dane sprzedawcy',
  seller_reviews: 'opinie sprzedawcy',
  battery: 'bateria',
  battery_health: 'kondycja baterii',
  battery_cycle_count: 'cykle baterii',
  authenticity: 'oryginalność',
  images: 'zdjęcia',
  description: 'opis',
  accessories: 'akcesoria',
}

export const gapLabel = (gap: string) => {
  const key = gap.replace(/_unknown$/, '')
  return gapNames[key] ?? key.replaceAll('_', ' ')
}

export const explanationParts = (explanation?: string | null): string[] =>
  (explanation ?? '')
    .split(';')
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .slice(0, 3)

const conditions: Record<string, string> = {
  new: 'nowe',
  like_new: 'jak nowe',
  very_good: 'bardzo dobry stan',
  good: 'dobry stan',
  fair: 'stan dostateczny',
  unknown: 'stan nieznany',
}

export const formatCondition = (value: string) => conditions[value] ?? value
