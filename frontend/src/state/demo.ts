import type { Candidate, Recommendation, RunResponse } from '../api/types'

export const demoCandidates: Candidate[] = [
  {
    product_id: 'demo-sony-wf-1000xm5',
    brand: 'Sony',
    model: 'WF-1000XM5',
    exact_variant: 'WF-1000XM5',
    estimated_price: 520,
    key_features: ['bardzo dobre ANC', 'ciepłe brzmienie', 'multipoint'],
    similarity_reasons: ['dokanalowe', 'mocne ANC', 'tryb transparentny'],
    differences: ['więcej ustawień dźwięku', 'większe etui'],
    why_it_fits: 'Najpełniejszy zamiennik AirPods Pro, jeśli priorytetem jest cisza.',
    tradeoff: 'Etui i aplikacja są mniej dyskretne niż w ekosystemie Apple.',
    confidence: 0.88,
    data_gaps: ['demo_product_research'],
  },
  {
    product_id: 'demo-samsung-buds2-pro',
    brand: 'Samsung',
    model: 'Galaxy Buds2 Pro',
    exact_variant: 'SM-R510',
    estimated_price: 310,
    key_features: ['ANC', 'lekka konstrukcja', '24-bit audio'],
    similarity_reasons: ['kompaktowe', 'dobry tryb kontaktu', 'wygodne'],
    differences: ['najlepiej działają z Androidem', 'krótsza bateria'],
    why_it_fits: 'Najlepszy stosunek ceny do jakości w tym zestawieniu.',
    tradeoff: 'Część funkcji jest ograniczona poza telefonami Samsung.',
    confidence: 0.84,
    data_gaps: ['demo_product_research'],
  },
  {
    product_id: 'demo-bose-qc-earbuds-ii',
    brand: 'Bose',
    model: 'QuietComfort Earbuds II',
    exact_variant: 'QC Earbuds II',
    estimated_price: 460,
    key_features: ['referencyjne ANC', 'pełny bas', 'dopasowanie końcówek'],
    similarity_reasons: ['flagowe ANC', 'tryb aware', 'premium'],
    differences: ['większe słuchawki', 'brak multipoint'],
    why_it_fits: 'Dla osoby, która chce przede wszystkim maksymalnego wyciszenia.',
    tradeoff: 'Są większe i mniej wygodne dla małych uszu.',
    confidence: 0.82,
    data_gaps: ['demo_product_research'],
  },
  {
    product_id: 'demo-nothing-ear-2',
    brand: 'Nothing',
    model: 'Ear (2)',
    exact_variant: 'B155',
    estimated_price: 250,
    key_features: ['ANC', 'lekka konstrukcja', 'wyróżniający wygląd'],
    similarity_reasons: ['podobny format', 'prosta obsługa', 'dobra mobilność'],
    differences: ['słabsze ANC', 'jaśniejsze brzmienie'],
    why_it_fits: 'Najtańszy sensowny kierunek bez rezygnacji z podstawowych funkcji.',
    tradeoff: 'Wyciszenie jest wyraźnie słabsze od AirPods Pro i Sony.',
    confidence: 0.78,
    data_gaps: ['demo_product_research'],
  },
]

const observedAt = '2026-07-11T12:00:00Z'

export const demoRecommendations: Recommendation[] = [
  {
    rank: 1,
    recommended: true,
    score: 87,
    score_breakdown: { product_match: 91, offer_quality: 88, seller_trust: 82, confidence: 0.86 },
    explanation: 'Właściwy wariant, bardzo dobry stan i cena wyraźnie niższa od nowego produktu.',
    listings: {
      source: 'demo',
      title: 'Sony WF-1000XM5, czarne, komplet',
      url: 'https://example.com/demo/sony-xm5-komplet',
      price: 479,
      currency: 'PLN',
      condition: 'very_good',
      exact_variant: 'WF-1000XM5',
      warranty: '3 miesiące gwarancji sprzedawcy',
      returns: '14 dni',
      location: 'Warszawa',
      retrieved_at: observedAt,
      data_gaps: ['battery_health_unknown'],
      confidence: 0.86,
    },
    source_url: 'https://example.com/demo/sony-xm5-komplet',
    retrieved_at: observedAt,
    confidence: 0.86,
    data_gaps: ['battery_health_unknown'],
    is_stale: false,
    field_availability: { seller_rating: '4.8/5', warranty: '3 miesiące', returns: '14 dni', authenticity: 'unknown', battery: 'unknown' },
  },
  {
    rank: 2,
    recommended: false,
    score: 81,
    score_breakdown: { product_match: 91, offer_quality: 80, seller_trust: 72, confidence: 0.78 },
    explanation: 'Najniższa cena za właściwy model, ale oferta ma mniej danych o sprzedawcy i baterii.',
    listings: {
      source: 'demo',
      title: 'Sony WF-1000XM5 z etui',
      url: 'https://example.com/demo/sony-xm5-tanio',
      price: 419,
      currency: 'PLN',
      condition: 'good',
      exact_variant: 'WF-1000XM5',
      warranty: null,
      returns: null,
      location: 'Kraków',
      retrieved_at: observedAt,
      data_gaps: ['seller_reviews_unknown', 'warranty_unknown', 'battery_health_unknown'],
      confidence: 0.78,
    },
    source_url: 'https://example.com/demo/sony-xm5-tanio',
    retrieved_at: observedAt,
    confidence: 0.78,
    data_gaps: ['seller_reviews_unknown', 'warranty_unknown', 'battery_health_unknown'],
    is_stale: false,
    field_availability: { seller_rating: 'unknown', warranty: 'unknown', returns: 'unknown', authenticity: 'unknown', battery: 'unknown' },
  },
  {
    rank: 3,
    recommended: false,
    score: 76,
    score_breakdown: { product_match: 91, offer_quality: 72, seller_trust: 94, confidence: 0.9 },
    explanation: 'Najbezpieczniejszy sprzedawca i roczna gwarancja, kosztem wyższej ceny.',
    listings: {
      source: 'demo',
      title: 'Sony WF-1000XM5 odnowione, 12 mies. gwarancji',
      url: 'https://example.com/demo/sony-xm5-gwarancja',
      price: 549,
      currency: 'PLN',
      condition: 'like_new',
      exact_variant: 'WF-1000XM5',
      warranty: '12 miesięcy',
      returns: '30 dni',
      location: 'wysyłka',
      retrieved_at: observedAt,
      data_gaps: ['battery_cycle_count_unknown'],
      confidence: 0.9,
    },
    source_url: 'https://example.com/demo/sony-xm5-gwarancja',
    retrieved_at: observedAt,
    confidence: 0.9,
    data_gaps: ['battery_cycle_count_unknown'],
    is_stale: false,
    field_availability: { seller_rating: '4.9/5', warranty: '12 miesięcy', returns: '30 dni', authenticity: 'potwierdzone przez sprzedawcę', battery: 'unknown' },
  },
]

export const demoRun: RunResponse = {
  id: 'demo-run',
  status: 'completed',
  recommendations: demoRecommendations,
  sources_succeeded: ['demo'],
  new_price_benchmark: {
    product_name: 'Sony WF-1000XM5',
    price: 799,
    currency: 'PLN',
    url: 'https://example.com/demo/sony-xm5-new',
    source: 'demo',
    retrieved_at: observedAt,
  },
}

export function demoRunForCandidate(candidate: Candidate): RunResponse {
  const labels = ['komplet', 'z etui', 'odnowione, 12 mies. gwarancji']
  const priceFactors = [0.92, 0.8, 1.04]
  const recommendations = demoRecommendations.map((recommendation, index) => {
    const listing = recommendation.listings
    if (!listing) return recommendation
    const url = `https://example.com/demo/${candidate.product_id}/${index + 1}`
    return {
      ...recommendation,
      listings: {
        ...listing,
        title: `${candidate.brand} ${candidate.model}, ${labels[index]}`,
        exact_variant: candidate.exact_variant ?? candidate.model,
        price: Math.round(candidate.estimated_price * priceFactors[index]),
        url,
      },
      source_url: url,
    }
  })
  return {
    ...demoRun,
    recommendations,
    new_price_benchmark: demoRun.new_price_benchmark
      ? {
          ...demoRun.new_price_benchmark,
          product_name: `${candidate.brand} ${candidate.model}`,
          price: Math.round(candidate.estimated_price * 1.5),
        }
      : null,
  }
}
