import type { Candidate } from '../api/types'
import { formatMoney } from '../state/presentation'
import { ElectronicsVisual } from './ElectronicsVisual'

export function ProductCard({ candidate, index }: { candidate: Candidate; index: number }) {
  return (
    <article className="product-card-content">
      <div className="product-media">
        {candidate.image_url ? <img src={candidate.image_url} alt={`${candidate.brand} ${candidate.model}`} /> : <ElectronicsVisual variant={index} />}
      </div>
      <div className="product-copy">
        <div className="product-heading"><div><p className="eyebrow">Używane · cena orientacyjna</p><h2>{candidate.brand} {candidate.model}</h2></div><strong>{formatMoney(candidate.estimated_price)}</strong></div>
        <p className="fit-copy">{candidate.why_it_fits}</p>
        <ul className="feature-list">{candidate.key_features.slice(0, 3).map((feature) => <li key={feature}>{feature}</li>)}</ul>
        <div className="tradeoff"><span>Kompromis</span><p>{candidate.tradeoff}</p></div>
      </div>
    </article>
  )
}
