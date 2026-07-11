import { describe, expect, it } from 'vitest'
import { dateTime, fieldLabel, money, scoreLabel, terminalStatus } from './presentation'
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

  it('keeps demo offers on the exact selected variant', () => {
    const candidate = demoCandidates[1]
    const run = demoRunForCandidate(candidate)
    expect(run.recommendations).toHaveLength(3)
    expect(run.recommendations.every((item) => item.listings?.exact_variant === candidate.exact_variant)).toBe(true)
    expect(run.new_price_benchmark?.product_name).toContain(candidate.model)
  })
})
