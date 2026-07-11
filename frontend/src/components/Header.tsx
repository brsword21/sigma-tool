import { Icon } from './Icons'

export function Header({ onReset, active }: { onReset: () => void; active: boolean }) {
  return (
    <header className="app-header">
      <button className="brand" onClick={onReset} aria-label="Sigma — zacznij od początku">Sigma<span>.</span></button>
      <div className="header-actions">
        {active && <button className="quiet-action" onClick={onReset}>Nowe wyszukiwanie</button>}
        <button className="icon-button integration-hook" disabled title="Historia będzie dostępna po podłączeniu logowania" aria-label="Historia — integracja w toku" data-integration="history"><Icon name="history" /></button>
        <button className="icon-button integration-hook" disabled title="Konto będzie dostępne po podłączeniu logowania" aria-label="Konto — integracja w toku" data-integration="account"><Icon name="user" /></button>
      </div>
    </header>
  )
}
