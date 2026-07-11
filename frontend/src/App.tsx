import { useEffect, useMemo, useRef, useState } from 'react'
import type { Candidate, SearchDirection } from './api/types'
import { useAuth } from './auth/AuthProvider'
import { AccountControls } from './components/AccountControls'
import { HistoryDrawer } from './components/HistoryDrawer'
import { LineWaves } from './components/LineWaves'
import { dateTime, fieldLabel, listingFor, money, scoreLabel, sourceName } from './state/presentation'
import { useShoppingSession } from './state/useShoppingSession'

const examplePrompts = [
  'Samsung S25 w dobrym stanie do 2200 zł',
  'Laptop do pracy z baterią powyżej 80%',
]

const directions: Array<{ value: SearchDirection; label: string }> = [
  { value: 'best_value', label: 'Najlepsza wartość' },
  { value: 'most_similar', label: 'Najbardziej podobne' },
  { value: 'best_quality', label: 'Najlepsza jakość' },
  { value: 'lowest_price', label: 'Najniższa cena' },
]

const humanCondition: Record<string, string> = {
  new: 'nowe',
  like_new: 'jak nowe',
  very_good: 'bardzo dobry',
  good: 'dobry',
  fair: 'dostateczny',
  unknown: 'brak danych',
}

function ElectronicsMark({ compact = false }: { compact?: boolean }) {
  return (
    <svg className={compact ? 'mark mark--compact' : 'mark'} viewBox="0 0 96 96" aria-hidden="true">
      <rect x="18" y="18" width="35" height="56" rx="7" />
      <path d="M31 65h9" />
      <path d="M62 33h9a7 7 0 0 1 7 7v31" />
      <path d="M58 71h24" />
      <circle cx="68" cy="23" r="7" />
    </svg>
  )
}

function ProductCard({ candidate, direction, onChoose, busy }: {
  candidate: Candidate
  direction: SearchDirection
  onChoose: (candidate: Candidate, direction: SearchDirection) => void
  busy: boolean
}) {
  return (
    <article className="product-card">
      <div className="product-card__visual">
        <span className="product-card__brand">{candidate.brand}</span>
        {candidate.image_url
          ? <img src={candidate.image_url} alt={`${candidate.brand} ${candidate.model}`} />
          : <ElectronicsMark />}
        <span className="confidence">pewność {Math.round(candidate.confidence * 100)}%</span>
      </div>
      <div className="product-card__content">
        <div className="product-card__heading">
          <div>
            <p className="eyebrow">Kierunek wyboru</p>
            <h3>{candidate.model}</h3>
          </div>
          <strong>{money(candidate.estimated_price)}</strong>
        </div>
        <p className="product-card__fit">{candidate.why_it_fits}</p>
        <ul className="feature-list" aria-label="Najważniejsze cechy">
          {candidate.key_features.slice(0, 3).map((feature) => <li key={feature}>{feature}</li>)}
        </ul>
        <div className="tradeoff">
          <span>Kompromis</span>
          <p>{candidate.tradeoff}</p>
        </div>
        <button className="button button--primary button--wide" type="button" disabled={busy} onClick={() => onChoose(candidate, direction)}>
          Sprawdź konkretne oferty
          <span aria-hidden="true">↗</span>
        </button>
      </div>
    </article>
  )
}

function ScoreRow({ label, value }: { label: string; value: unknown }) {
  const numeric = Number(value)
  const valid = Number.isFinite(numeric)
  return (
    <div className="score-row">
      <span>{label}</span>
      <div className="score-track" aria-hidden="true">
        <i style={{ width: valid ? `${Math.max(4, Math.min(100, numeric))}%` : '0%' }} />
      </div>
      <strong>{scoreLabel(value)}</strong>
    </div>
  )
}

function App() {
  const shopping = useShoppingSession()
  const auth = useAuth()
  const [draft, setDraft] = useState('')
  const [direction, setDirection] = useState<SearchDirection>('best_value')
  const [historyOpen, setHistoryOpen] = useState(false)
  const previousUserId = useRef<string | null>(auth.user?.id ?? null)
  const visibleMessages = useMemo(() => shopping.messages.slice(-5), [shopping.messages])

  useEffect(() => {
    const nextUserId = auth.user?.id ?? null
    if (previousUserId.current !== nextUserId) {
      shopping.reset()
      setDraft('')
      setHistoryOpen(false)
      previousUserId.current = nextUserId
    }
  }, [auth.user?.id, shopping.reset])

  const send = async () => {
    const text = draft.trim()
    if (!text) return
    setDraft('')
    await shopping.submit(text)
  }

  return (
    <div className={`app phase-${shopping.phase}`}>
      <LineWaves />
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Picky — początek">
          <span className="brand__symbol">P</span>
          <span>Picky</span>
        </a>
        <div className="topbar__right">
          <div className={`topbar__status ${shopping.busy ? 'topbar__status--working' : ''}`} role="status" aria-live="polite">
            <span className="status-dot" aria-hidden="true" />
            {shopping.busy ? 'agent działa' : shopping.demoMode ? 'dane demonstracyjne' : 'agent gotowy'}
          </div>
          <AccountControls onOpenHistory={() => setHistoryOpen(true)} />
        </div>
      </header>

      {shopping.demoMode && (
        <div className="demo-banner" role="status">
          <strong>Tryb demonstracyjny</strong>
          <span>Przygotowane dane są wyraźnie oddzielone od ofert live.</span>
        </div>
      )}

      <main id="top" className="workspace">
        <section className="conversation" aria-label="Rozmowa z Picky">
          <div className="conversation__intro">
            <p className="eyebrow">Agent do używanej elektroniki</p>
            <h1>Znajdź elektronikę,<br /><em>którą warto kupić.</em></h1>
            <p>Powiedz, czego potrzebujesz albo co Ci się podoba. Zamiast setek wyników dostaniesz kilka decyzji z dowodami.</p>
          </div>

          {visibleMessages.length > 0 && (
            <div className="messages" aria-live="polite">
              {visibleMessages.map((item) => (
                <div className={`message message--${item.role}`} key={item.id}>
                  <span>{item.role === 'assistant' ? 'Picky' : 'Ty'}</span>
                  <p>{item.content}</p>
                </div>
              ))}
              {shopping.busy && (
                <div className="message message--assistant message--working" role="status" aria-label="Picky pracuje">
                  <span>Picky</span>
                  <p><i className="thinking-spinner" aria-hidden="true" /></p>
                </div>
              )}
            </div>
          )}

          {shopping.phase === 'idle' && (
            <div className="examples" aria-label="Przykładowe pytania">
              {examplePrompts.map((prompt) => (
                <button key={prompt} type="button" onClick={() => setDraft(prompt)}>
                  <span>{prompt}</span><i aria-hidden="true">↗</i>
                </button>
              ))}
            </div>
          )}

          <div className="composer-wrap">
            <div className="composer">
              <button className="attach" type="button" disabled title="Zdjęcia dodamy po demo" aria-label="Dodawanie zdjęć będzie dostępne później">＋</button>
              <textarea
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault()
                    void send()
                  }
                }}
                rows={1}
                maxLength={2000}
                placeholder={shopping.phase === 'results' ? 'Zmień priorytet, np. ważniejsza jest gwarancja…' : 'Opisz potrzebę albo podaj model…'}
                disabled={shopping.busy}
                aria-label="Wiadomość do Picky"
              />
              <button className="send" type="button" disabled={!draft.trim() || shopping.busy} onClick={() => void send()} aria-label="Wyślij wiadomość">↑</button>
            </div>
            <p className="composer-note">Picky pokazuje źródła i jawnie oznacza braki danych.</p>
          </div>
        </section>

        <section className="decision" aria-label="Wyniki wyszukiwania">
          {shopping.phase === 'idle' || shopping.phase === 'conversing' ? (
            <div className="decision-empty">
              <div className="orb"><ElectronicsMark /></div>
              <p>Jedna potrzeba.<br />Kilka sprawdzonych kierunków.<br /><strong>Jedna decyzja.</strong></p>
              <div className="evidence-note"><span>01</span><p>Najpierw rozumiemy produkt. Pełne wyszukiwanie rusza dopiero po Twoim wyborze.</p></div>
            </div>
          ) : null}

          {shopping.phase === 'selecting' && (
            <div className="selection">
              <div className="section-heading">
                <div><p className="eyebrow">Etap 1 · wybierz kierunek</p><h2>{shopping.candidates.length} modele, które mają sens</h2></div>
                <span>To nie jest jeszcze ranking ofert</span>
              </div>
              <div className="direction-picker" aria-label="Kierunek rankingu">
                {directions.map((item) => (
                  <button className={direction === item.value ? 'active' : ''} key={item.value} type="button" onClick={() => setDirection(item.value)}>{item.label}</button>
                ))}
              </div>
              <div className="product-grid">
                {shopping.candidates.map((candidate) => <ProductCard key={candidate.product_id} candidate={candidate} direction={direction} onChoose={shopping.choose} busy={shopping.busy} />)}
              </div>
            </div>
          )}

          {shopping.phase === 'searching' && (
            <div className="search-state" aria-live="polite">
              <div className="search-rings"><ElectronicsMark /></div>
              <p className="eyebrow">Etap 2 · konkretne oferty</p>
              <h2>{shopping.run?.status === 'running'
                ? <>Weryfikuję oferty,<br />ceny i dokładny model.</>
                : <>Uruchamiam źródła<br />dla wybranego modelu.</>}</h2>
              <ul>
                <li className="done">Rozpoznanie wybranego modelu</li>
                <li className={shopping.run?.status === 'running' ? 'done' : 'active'}>Połączenie ze źródłami ofert</li>
                <li className={shopping.run?.status === 'running' ? 'active' : ''}>Odrzucanie obcych modeli i akcesoriów</li>
              </ul>
            </div>
          )}

          {shopping.phase === 'error' && (
            <div className="error-state" role="alert">
              <span className="error-state__mark">!</span>
              <p className="eyebrow">Nie kończymy na pustym ekranie</p>
              <h2>Nie udało się pobrać pewnych wyników.</h2>
              <p>{shopping.error}</p>
              <div className="error-actions">
                <button className="button button--primary" type="button" onClick={() => void shopping.retry()} disabled={shopping.busy}>Spróbuj ponownie</button>
                <button className="button button--secondary" type="button" onClick={shopping.useDemo}>Uruchom dane demonstracyjne</button>
              </div>
            </div>
          )}

          {shopping.phase === 'results' && shopping.run && (
            <div className="results">
              <div className="section-heading results__heading">
                <div>
                  <p className="eyebrow">Etap 2 · ranking ofert</p>
                  <h2>{shopping.selected?.model ?? 'Najlepsze dopasowania'}</h2>
                </div>
                {shopping.run.new_price_benchmark && <div className="benchmark"><span>Nowe od</span><strong>{money(shopping.run.new_price_benchmark.price, shopping.run.new_price_benchmark.currency)}</strong></div>}
              </div>

              {shopping.run.status === 'partial' && (
                <div className="partial" role="status"><strong>Częściowy wynik.</strong> Część źródeł jest chwilowo niedostępna; pokazujemy tylko dane, które udało się potwierdzić.</div>
              )}

              <div className="offers">
                {shopping.recommendations.map((recommendation, index) => {
                  const listing = listingFor(recommendation)
                  if (!listing) return null
                  const gaps = recommendation.data_gaps.length ? recommendation.data_gaps : listing.data_gaps ?? []
                  return (
                    <article className={`offer ${index === 0 ? 'offer--recommended' : ''}`} key={`${recommendation.rank}-${listing.url}`}>
                      <div className="offer__index">{String(index + 1).padStart(2, '0')}</div>
                      <div className="offer__body">
                        <div className="offer__top">
                          <div>
                            <div className="offer__badges">
                              {index === 0 && <span className="badge badge--best">Najlepszy wybór</span>}
                              <span className="badge">{sourceName(recommendation)}</span>
                              {recommendation.is_stale && <span className="badge badge--warn">starszy cache</span>}
                            </div>
                            <h3>{listing.title}</h3>
                            <p>{fieldLabel(listing.exact_variant)} · stan: {humanCondition[listing.condition] ?? listing.condition}</p>
                          </div>
                          <div className="offer__price"><strong>{money(listing.price, listing.currency)}</strong><span>{fieldLabel(listing.location)}</span></div>
                        </div>

                        <div className="evidence-grid">
                          <div className="scores">
                            <ScoreRow label="Dopasowanie produktu" value={recommendation.score_breakdown.product_match} />
                            <ScoreRow label="Jakość oferty" value={recommendation.score_breakdown.offer_quality} />
                            <ScoreRow label="Sprzedawca" value={recommendation.score_breakdown.seller_trust} />
                          </div>
                          <div className="verdict"><span>Dlaczego ta oferta</span><p>{recommendation.explanation ?? 'Dobra równowaga ceny, stanu i kompletności danych.'}</p></div>
                        </div>

                        <div className="trust-strip">
                          <div><span>Gwarancja</span><strong>{fieldLabel(recommendation.field_availability.warranty)}</strong></div>
                          <div><span>Zwrot</span><strong>{fieldLabel(recommendation.field_availability.returns)}</strong></div>
                          <div><span>Bateria / zasilanie</span><strong>{fieldLabel(recommendation.field_availability.battery)}</strong></div>
                          <div><span>Pobrano</span><strong>{dateTime(recommendation.retrieved_at ?? listing.retrieved_at)}</strong></div>
                        </div>

                        {gaps.length > 0 && <div className="gaps"><strong>Nie wiemy:</strong> {gaps.map((gap) => gap.replaceAll('_', ' ')).join(' · ')}</div>}

                        <div className="offer__footer">
                          <span>Pewność danych {Math.round(recommendation.confidence * 100)}%</span>
                          <a className="button button--primary" href={recommendation.source_url ?? listing.url} target="_blank" rel="noreferrer noopener">Zobacz ofertę <span aria-hidden="true">↗</span></a>
                        </div>
                      </div>
                    </article>
                  )
                })}
              </div>
            </div>
          )}
        </section>
      </main>
      {auth.status === 'signed-in' && (
        <HistoryDrawer
          open={historyOpen}
          onClose={() => setHistoryOpen(false)}
          onNewChat={() => { shopping.reset(); setDraft('') }}
          onRestore={(history) => { shopping.restoreHistory(history); setDraft('') }}
        />
      )}
    </div>
  )
}

export { App }
