import type { Recommendation, RunResponse } from '../api/types'
import { clampScore, formatCondition, formatGap, formatMoney, formatRetrievedAt } from '../state/presentation'
import { Icon } from './Icons'

function TrustRow({ label, value, unknown = false }: { label: string; value?: number; unknown?: boolean }) {
  const score = clampScore(value)
  return <div className="trust-row"><span>{label}</span><div className="score-track"><i style={{ width: `${score}%` }}/></div><strong>{unknown ? 'Brak danych' : `${score}/100`}</strong></div>
}

function Offer({ item, position }: { item: Recommendation; position: number }) {
  const listing = item.listings ?? item.listing
  if (!listing) return null
  const breakdown = item.score_breakdown
  const gaps = [...new Set([...(item.data_gaps ?? []), ...(listing.data_gaps ?? [])])]
  return (
    <article className={`offer ${position === 0 ? 'offer--recommended' : ''}`}>
      <div className="offer-rank"><span>{position === 0 ? 'Najlepszy wybór' : `#${position + 1}`}</span><strong>{Math.round(item.score)}<small>/100</small></strong></div>
      <div className="offer-main">
        <div className="offer-title"><div><p>{listing.source} · {formatCondition(listing.condition)}</p><h2>{listing.title}</h2></div><strong>{formatMoney(listing.price, listing.currency)}</strong></div>
        <p className="offer-explanation">{item.explanation || 'Oferta spełnia wymagania dla wybranego modelu.'}</p>
        <div className="trust-grid">
          <TrustRow label="Dopasowanie produktu" value={breakdown.product_match}/>
          <TrustRow label="Jakość oferty" value={breakdown.offer_quality}/>
          <TrustRow label="Sprzedawca" value={breakdown.seller_trust} unknown={gaps.includes('seller_signals')}/>
        </div>
        {gaps.length > 0 && <div className="risk-box"><strong>{item.is_stale ? 'Wynik wymaga odświeżenia' : 'Sprawdź przed zakupem'}</strong><ul>{gaps.slice(0, 4).map((gap) => <li key={gap}>{formatGap(gap)}</li>)}</ul></div>}
        <div className="offer-footer"><span>{formatRetrievedAt(item.retrieved_at ?? listing.retrieved_at)}</span><a href={item.source_url ?? listing.url} target="_blank" rel="noreferrer">Zobacz ofertę <Icon name="external" /></a></div>
      </div>
    </article>
  )
}

export function OfferRanking({ run }: { run: RunResponse }) {
  return (
    <section className="ranking" aria-labelledby="ranking-title">
      <header className="ranking-header"><div><p className="eyebrow">Ranking konkretnych ofert</p><h1 id="ranking-title">Ta opcja daje najlepszy bilans.</h1><p>{run.status === 'partial' ? 'Część źródeł nie odpowiedziała. Dostępne wyniki są oznaczone zgodnie z poziomem pewności.' : `Porównano ${run.recommendations.length} oferty właściwego wariantu.`}</p></div>{run.new_price_benchmark && <div className="benchmark"><span>Nowy egzemplarz</span><strong>{formatMoney(run.new_price_benchmark.price, run.new_price_benchmark.currency)}</strong><a href={run.new_price_benchmark.url} target="_blank" rel="noreferrer">Porównaj punkt odniesienia</a></div>}</header>
      <div className="offer-list">{run.recommendations.map((item, index) => <Offer key={`${item.rank}-${item.source_url}`} item={item} position={index}/>)}</div>
    </section>
  )
}
