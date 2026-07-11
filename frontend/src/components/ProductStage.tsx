import type { Candidate, SearchDirection } from '../api/types'
import { Icon } from './Icons'
import { ProductCard } from './ProductCard'

const directions: { value: SearchDirection; label: string }[] = [
  { value: 'best_value', label: 'Najlepsza wartość' },
  { value: 'most_similar', label: 'Najbardziej podobne' },
  { value: 'best_quality', label: 'Najlepsza jakość' },
  { value: 'lowest_price', label: 'Najniższa cena' },
]

export function ProductStage({ candidates, selectedIndex, direction, onSelect, onDirection, onCompare, onCheapest, onNext, onRemove }: {
  candidates: Candidate[]; selectedIndex: number; direction: SearchDirection
  onSelect: (index: number) => void; onDirection: (direction: SearchDirection) => void; onCompare: () => void
  onCheapest: () => void; onNext: () => void; onRemove: () => void
}) {
  const selected = candidates[selectedIndex]
  if (!selected) return <div className="empty-stage"><p>Nie ma więcej propozycji.</p><span>Zmień opis potrzeby, aby rozpocząć nowe wyszukiwanie.</span></div>
  return (
    <section className="focus-mode" aria-label="Wybór produktu">
      <div className="focus-meta"><span>{selectedIndex + 1} z {candidates.length}</span><p>Wybierz model, a Sigma sprawdzi konkretne oferty.</p></div>
      <div className="deck">
        {candidates.map((candidate, index) => (
          <button key={candidate.product_id} className={`deck-peek ${index === selectedIndex ? 'is-active' : ''}`} style={{ '--offset': index - selectedIndex } as React.CSSProperties} onClick={() => onSelect(index)} aria-label={`Wybierz ${candidate.brand} ${candidate.model}`} tabIndex={index === selectedIndex ? -1 : 0}>
            {index === selectedIndex && <ProductCard candidate={candidate} index={index} />}
          </button>
        ))}
      </div>
      <div className="decision-panel">
        <div className="direction-picker" role="group" aria-label="Kierunek porównania">
          {directions.map((item) => <button key={item.value} className={direction === item.value ? 'is-selected' : ''} onClick={() => onDirection(item.value)}>{item.label}</button>)}
        </div>
        <div className="decision-actions">
          <button className="round-action" onClick={onCheapest} title="Pokaż tańszy model"><Icon name="shuffle"/><span>Tańszy</span></button>
          <button className="round-action" onClick={onNext} title="Pokaż kolejny wariant"><Icon name="refresh"/><span>Inny</span></button>
          <button className="primary-action" onClick={onCompare}>Porównaj oferty <Icon name="chevron" /></button>
          <button className="round-action" onClick={onRemove} title="Pomiń ten model"><Icon name="trash"/><span>Pomiń</span></button>
        </div>
      </div>
    </section>
  )
}
