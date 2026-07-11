import type { ChatMessage } from '../state/useShoppingSession'

export function Conversation({ messages, compact = false }: { messages: ChatMessage[]; compact?: boolean }) {
  if (!messages.length) return null
  const visible = compact ? messages.slice(-2) : messages
  return (
    <section className={`conversation ${compact ? 'conversation--compact' : ''}`} aria-label="Rozmowa z Picky">
      {visible.map((message) => (
        <div key={message.id} className={`message message--${message.role}`}>
          <span className="message-author">{message.role === 'assistant' ? 'Picky' : 'Ty'}</span>
          <p>{message.content}</p>
        </div>
      ))}
    </section>
  )
}
