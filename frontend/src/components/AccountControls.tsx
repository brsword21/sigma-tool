import { useState } from 'react'
import { useAuth } from '../auth/AuthProvider'
import { AuthModal } from './AuthModal'

export function AccountControls({ onOpenHistory }: { onOpenHistory: () => void }) {
  const auth = useAuth()
  const [loginOpen, setLoginOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [error, setError] = useState('')

  if (auth.status !== 'signed-in') {
    return (
      <>
        <button className="account-button" type="button" onClick={() => setLoginOpen(true)} disabled={auth.status === 'loading'}>
          <span className="account-avatar" aria-hidden="true">{auth.status === 'loading' ? '·' : 'P'}</span>
          <span>{auth.status === 'loading' ? 'Sprawdzam konto' : 'Zaloguj się'}</span>
        </button>
        <AuthModal open={loginOpen} onClose={() => setLoginOpen(false)} />
      </>
    )
  }

  const email = auth.user?.email ?? 'Twoje konto'
  return (
    <div className="account-controls">
      <button className="history-button" type="button" onClick={onOpenHistory}>
        <span aria-hidden="true">↺</span> Historia
      </button>
      <button className="account-button" type="button" aria-expanded={menuOpen} onClick={() => setMenuOpen((current) => !current)}>
        <span className="account-avatar" aria-hidden="true">{email.slice(0, 1).toUpperCase()}</span>
        <span className="account-email">{email}</span>
      </button>
      {menuOpen && (
        <div className="account-menu">
          <span>Zalogowano jako</span>
          <strong>{email}</strong>
          {error && <p role="alert">{error}</p>}
          <button type="button" onClick={() => {
            setError('')
            void auth.signOut().catch((reason) => setError(reason instanceof Error ? reason.message : 'Nie udało się wylogować.'))
          }}>Wyloguj się</button>
        </div>
      )}
    </div>
  )
}
