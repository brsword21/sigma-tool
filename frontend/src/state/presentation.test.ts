import { describe, expect, it } from 'vitest'
import { batteryHealth, capacityLabel, dateTime, explanationParts, fieldLabel, gapLabel, money, savingsVsNew, scoreLabel, terminalStatus } from './presentation'
import type { Listing } from '../api/types'
import { demoCandidates, demoRunForCandidate } from './demo'

describe('presentation helpers', () => {
  it('formats Polish prices and missing values', () => {
    expect(money(479)).toContain('479')
    expect(fieldLabel('unknown')).toBe('Brak danych')
    expect(fieldLabel('12 miesięcy')).toBe('12 miesięcy')
  })

  it('classifies scores without fake precision', () => {
    expect(scoreLabel(91)).toBe('Mocne')
    expect(scoreLabel(66)).toBe('Dobre')
    expect(scoreLabel(undefined)).toBe('Brak danych')
  })

  it('recognizes only terminal run states', () => {
    expect(terminalStatus('completed')).toBe(true)
    expect(terminalStatus('partial')).toBe(true)
    expect(terminalStatus('failed')).toBe(true)
    expect(terminalStatus('running')).toBe(false)
  })

  it('does not invent invalid dates', () => {
    expect(dateTime('not-a-date')).toBe('Brak daty')
  })

  it('extracts listing facts from real OLX-style titles', () => {
    const listing = (title: string): Listing => ({ source: 'olx', title, url: 'https://x', price: 1999, currency: 'PLN', condition: 'good' })
    expect(batteryHealth(listing('Telefon Apple iPhone 15 6GB/256GB 85% bat Poznań'))).toBe(85)
    expect(batteryHealth(listing('Apple IPhone 15 256 Gb 88% kondycji Czarny'))).toBe(88)
    expect(batteryHealth(listing('APPLE IPHONE 15 128 GB | Jak Nowy, 87% Baterii'))).toBe(87)
    expect(batteryHealth(listing('iPhone 15 100% oryginał'))).toBeNull()
    expect(capacityLabel(listing('Apple IPhone 15 256 Gb 88% kondycji'))).toBe('256 GB')
    expect(capacityLabel(listing('Sony WF-1000XM5 czarne'))).toBeNull()
  })

  it('describes savings, gaps and explanations without noise', () => {
    expect(savingsVsNew(1999, 2549)).toBe('22% taniej niż nowy')
    expect(savingsVsNew(2500, 2549)).toBeNull()
    expect(savingsVsNew(1999, undefined)).toBeNull()
    expect(gapLabel('battery_health_unknown')).toBe('kondycja baterii')
    expect(gapLabel('seller_reviews')).toBe('opinie sprzedawcy')
    expect(explanationParts('cena 12% poniżej mediany; gwarancja: 12 miesięcy; a; b')).toHaveLength(3)
    expect(explanationParts(null)).toEqual([])
  })

  it('keeps demo offers on the exact selected variant', () => {
    const candidate = demoCandidates[1]
    const run = demoRunForCandidate(candidate)
    expect(run.recommendations).toHaveLength(3)
    expect(run.recommendations.every((item) => item.listings?.exact_variant === candidate.exact_variant)).toBe(true)
    expect(run.new_price_benchmark?.product_name).toContain(candidate.model)
  })
})
