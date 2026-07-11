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

const conditions: Record<string, string> = {
  new: 'nowe',
  like_new: 'jak nowe',
  very_good: 'bardzo dobry stan',
  good: 'dobry stan',
  fair: 'stan dostateczny',
  unknown: 'stan nieznany',
}

export const formatCondition = (value: string) => conditions[value] ?? value
