import { useEffect, useState } from 'react'
import { ElectronicsVisual } from './ElectronicsVisual'

const labels = ['Sprawdzam dokładne warianty', 'Porównuję ceny i stan', 'Oceniam sprzedawców', 'Układam rekomendację']

export function SearchProgress({ productName }: { productName?: string }) {
  const [step, setStep] = useState(0)
  useEffect(() => {
    const timer = window.setInterval(() => setStep((current) => Math.min(current + 1, labels.length - 1)), 4500)
    return () => window.clearInterval(timer)
  }, [])
  return (
    <section className="search-progress" aria-live="polite">
      <div className="search-visual"><ElectronicsVisual variant={0}/><span className="scan-line" /></div>
      <div className="search-copy"><span className="working-dot"/><p>{labels[step]}</p><h1>{productName ?? 'Wybrany model'}</h1><span>To może potrwać kilkadziesiąt sekund.</span></div>
      <ol>{labels.map((label, index) => <li key={label} className={index <= step ? 'is-done' : ''}><span>{index < step ? '✓' : index + 1}</span>{label}</li>)}</ol>
    </section>
  )
}
