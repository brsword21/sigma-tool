import { useEffect, useRef, useState } from 'react'
import { Icon } from './Icons'

export function Composer({ onSubmit, busy, compact = false }: { onSubmit: (text: string) => void; busy: boolean; compact?: boolean }) {
  const [value, setValue] = useState('')
  const input = useRef<HTMLTextAreaElement>(null)
  useEffect(() => {
    if (!compact) input.current?.focus()
  }, [compact])

  const submit = () => {
    if (!value.trim() || busy) return
    onSubmit(value)
    setValue('')
  }
  return (
    <form className={`composer ${compact ? 'composer--compact' : ''}`} onSubmit={(event) => { event.preventDefault(); submit() }}>
      <button type="button" className="composer-icon is-disabled" disabled title="Obsługa zdjęć pojawi się wkrótce" aria-label="Dodawanie zdjęć — wkrótce"><Icon name="paperclip" /></button>
      <textarea
        ref={input}
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit() } }}
        rows={1}
        maxLength={2000}
        placeholder={compact ? 'Zmień priorytet, np. „ważniejsza jest gwarancja”' : 'Czego szukasz?'}
        aria-label="Opisz, czego szukasz"
      />
      <button className="send-button" disabled={!value.trim() || busy} aria-label="Wyślij"><Icon name="arrow" /></button>
    </form>
  )
}
