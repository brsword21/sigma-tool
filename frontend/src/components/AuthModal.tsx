import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useAuth } from '../auth/AuthProvider'

export function AuthModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const auth = useAuth()
  const inputRef = useRef<HTMLInputElement>(null)
  const [email, setEmail] = useState('')
  const [state, setState] = useState<'idle' | 'sending' | 'sent' | 'error'>('idle')
  const [error, setError] = useState('')

  useEffect(() => {
    if (!open) return
    setState('idle')
    setError('')
    window.setTimeout(() => inputRef.current?.focus(), 30)
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [open, onClose])

  if (!open) return null

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setState('sending')
    setError('')
    try {
      await auth.signInWithMagicLink(email.trim())
      setState('sent')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Nie udało się wysłać linku.')
      setState('error')
    }
  }

  return (
    <div className="overlay" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="auth-modal" role="dialog" aria-modal="true" aria-labelledby="auth-title">
        <button className="close-button" type="button" onClick={onClose} aria-label="Zamknij logowanie">×</button>
        <div className="auth-modal__mark" aria-hidden="true">P</div>
        {state === 'sent' ? (
          <div className="auth-success" role="status">
            <p className="eyebrow">Link wysłany</p>
            <h2 id="auth-title">Sprawdź swoją skrzynkę.</h2>
            <p>Wysłaliśmy bezpieczny link na <strong>{email}</strong>. Otwórz go w tej przeglądarce, aby wrócić do Picky.</p>
            <button className="button button--primary button--wide" type="button" onClick={onClose}>Wróć do rozmowy</button>
          </div>
        ) : (
          <>
            <p className="eyebrow">Twoje decyzje zostają z Tobą</p>
            <h2 id="auth-title">Zaloguj się jednym linkiem.</h2>
            <p className="auth-modal__lead">Bez hasła. Po zalogowaniu nowe rozmowy zapiszą się w prywatnej historii.</p>
            <form onSubmit={(event) => void submit(event)}>
              <label htmlFor="login-email">Adres e-mail</label>
              <input ref={inputRef} id="login-email" type="email" autoComplete="email" required maxLength={254} value={email} onChange={(event) => setEmail(event.target.value)} placeholder="ty@firma.pl" />
              {state === 'error' && <p className="form-error" role="alert">{error}</p>}
              {!auth.configured && <p className="form-error" role="alert">Dodaj publiczną konfigurację Supabase do środowiska frontendu.</p>}
              <button className="button button--primary button--wide" type="submit" disabled={state === 'sending' || !auth.configured}>
                {state === 'sending' ? 'Wysyłam link…' : 'Wyślij link do logowania'}
              </button>
            </form>
            <p className="auth-modal__privacy">Historia jest dostępna tylko dla zalogowanego konta. Rozmowy gościa nie są przenoszone.</p>
          </>
        )}
      </section>
    </div>
  )
}
