import { useEffect, useState } from 'react'
import { getSessionHistory, listHistory } from '../api/client'
import type { HistorySession, SessionHistoryResponse } from '../api/types'

const titleFor = (session: HistorySession) => session.message_summary?.trim() || 'Rozmowa bez tytułu'

const dateFor = (session: HistorySession) => {
  const value = session.updated_at ?? session.created_at
  if (!value) return 'Ostatnia rozmowa'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Ostatnia rozmowa'
  return new Intl.DateTimeFormat('pl-PL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(date)
}

export function HistoryDrawer({
  open,
  onClose,
  onNewChat,
  onRestore,
}: {
  open: boolean
  onClose: () => void
  onNewChat: () => void
  onRestore: (history: SessionHistoryResponse) => void
}) {
  const [sessions, setSessions] = useState<HistorySession[]>([])
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [openingId, setOpeningId] = useState<string | null>(null)

  useEffect(() => {
    if (!open) return
    setState('loading')
    void listHistory()
      .then((response) => {
        setSessions(response.sessions)
        setState('ready')
      })
      .catch(() => setState('error'))
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [open, onClose])

  if (!open) return null

  const restore = async (session: HistorySession) => {
    setOpeningId(session.id)
    try {
      onRestore(await getSessionHistory(session.id))
      onClose()
    } catch {
      setState('error')
    } finally {
      setOpeningId(null)
    }
  }

  return (
    <div className="drawer-layer" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <aside className="history-drawer" role="dialog" aria-modal="true" aria-labelledby="history-title">
        <header className="history-drawer__header">
          <div><p className="eyebrow">Pamięć Picky</p><h2 id="history-title">Twoje rozmowy</h2></div>
          <button className="close-button" type="button" onClick={onClose} aria-label="Zamknij historię">×</button>
        </header>
        <button className="button button--primary button--wide" type="button" onClick={() => { onNewChat(); onClose() }}>＋ Nowa rozmowa</button>

        <div className="history-list" aria-live="polite">
          {state === 'loading' && <div className="history-state"><i className="history-spinner" /><p>Odczytuję zapisane decyzje…</p></div>}
          {state === 'error' && <div className="history-state history-state--error"><strong>Nie udało się wczytać historii.</strong><p>Zamknij panel i spróbuj ponownie. Możesz nadal rozpocząć nową rozmowę.</p></div>}
          {state === 'ready' && sessions.length === 0 && <div className="history-state"><span className="history-empty-mark">↺</span><strong>Tu pojawią się Twoje rozmowy.</strong><p>Pierwsza wiadomość wysłana po zalogowaniu automatycznie utworzy zapis.</p></div>}
          {state === 'ready' && sessions.map((session) => (
            <button className="history-item" type="button" key={session.id} disabled={openingId === session.id} onClick={() => void restore(session)}>
              <span className="history-item__dot" aria-hidden="true" />
              <span><strong>{titleFor(session)}</strong><small>{openingId === session.id ? 'Otwieram…' : dateFor(session)}</small></span>
              <i aria-hidden="true">→</i>
            </button>
          ))}
        </div>
        <p className="history-drawer__foot">Rozmowy gościa nie trafiają do tego profilu.</p>
      </aside>
    </div>
  )
}
