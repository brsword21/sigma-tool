import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, createSession, getRun, selectProduct, sendMessage } from '../api/client'
import type { Candidate, Recommendation, RunResponse, SearchDirection } from '../api/types'
import type { SessionHistoryResponse } from '../api/types'
import { demoCandidates, demoRun, demoRunForCandidate } from './demo'
import { terminalStatus } from './presentation'

export type ShoppingPhase = 'idle' | 'conversing' | 'selecting' | 'searching' | 'results' | 'error'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const message = (role: ChatMessage['role'], content: string): ChatMessage => ({
  id: crypto.randomUUID(),
  role,
  content,
})

const pause = (milliseconds: number) =>
  new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds))

export function useShoppingSession() {
  const [phase, setPhase] = useState<ShoppingPhase>('idle')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [selected, setSelected] = useState<Candidate | null>(null)
  const [run, setRun] = useState<RunResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [demoMode, setDemoMode] = useState(false)
  const [busy, setBusy] = useState(false)
  const sessionId = useRef<string | null>(null)
  const activeRequest = useRef(0)
  const lastOperation = useRef<(() => Promise<void>) | null>(null)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
      activeRequest.current += 1
    }
  }, [])

  const fail = useCallback((reason: unknown) => {
    const content = reason instanceof Error ? reason.message : 'Nie udało się ukończyć wyszukiwania.'
    setError(content)
    setPhase('error')
    setBusy(false)
  }, [])

  const pollRun = useCallback(async (runId: string) => {
    if (!runId) throw new Error('Brak identyfikatora wyszukiwania.')
    const requestId = ++activeRequest.current
    const deadline = Date.now() + 90_000
    setPhase('searching')
    setBusy(true)
    let emptyTerminalPolls = 0

    while (Date.now() < deadline) {
      if (requestId !== activeRequest.current) return

      let next
      try {
        next = await getRun(runId)
      } catch (reason) {
        if (reason instanceof ApiError && reason.status === 408) {
          await pause(1000)
          continue
        }
        throw reason
      }

      if (!mounted.current) {
        setBusy(false)
        return
      }
      if (requestId !== activeRequest.current) return

      setRun(next)

      if (terminalStatus(next.status)) {
        if (next.status === 'failed') {
          throw new Error('Nie znaleźliśmy teraz wystarczająco pewnych ofert.')
        }
        if (next.recommendations.length === 0) {
          emptyTerminalPolls += 1
          if (emptyTerminalPolls < 4) {
            await pause(1000)
            continue
          }
          throw new Error('Nie znaleźliśmy teraz wystarczająco pewnych ofert.')
        }
        setPhase('results')
        setBusy(false)
        return
      }

      emptyTerminalPolls = 0
      await pause(1500)
    }

    throw new Error('Wyszukiwanie trwa dłużej niż zwykle. Możesz spróbować ponownie.')
  }, [])

  const performSubmit = useCallback(async (text: string, appendUser = true) => {
    setError(null)
    setBusy(true)
    if (appendUser) setMessages((current) => [...current, message('user', text)])

    if (demoMode) {
      const baseRun = selected ? demoRunForCandidate(selected) : demoRun
      const warrantyFirst = text.toLocaleLowerCase('pl').includes('gwaranc')
      const recommendations = warrantyFirst
        ? [baseRun.recommendations[2], baseRun.recommendations[0], baseRun.recommendations[1]].map((item, index) => ({ ...item, rank: index + 1, recommended: index === 0 }))
        : baseRun.recommendations
      setRun({ ...baseRun, recommendations })
      setMessages((current) => [...current, message('assistant', warrantyFirst ? 'Przesunęłam ofertę z roczną gwarancją na pierwsze miejsce.' : 'Zaktualizowałam ranking na danych demonstracyjnych.')])
      setPhase('results')
      setBusy(false)
      return
    }

    try {
      const id = sessionId.current ?? (await createSession()).session_id
      sessionId.current = id
      const response = await sendMessage(id, text)
      if (response.run_id) {
        setMessages((current) => [...current, message(
          'assistant',
          response.direct_search
            ? 'Szukam teraz konkretnych ofert dla wskazanego modelu.'
            : 'Aktualizuję ranking bez pobierania ofert od początku.',
        )])
        await pollRun(response.run_id)
      } else if (response.question) {
        setCandidates([])
        setMessages((current) => [...current, message('assistant', response.question ?? '')])
        setPhase('conversing')
        setBusy(false)
      } else if (response.candidates.length >= 4) {
        setCandidates(response.candidates)
        setMessages((current) => [...current, message('assistant', `Mam ${response.candidates.length} kierunki. Wybierz ten, który najlepiej oddaje Twój priorytet.`)])
        setPhase('selecting')
        setBusy(false)
      } else {
        throw new Error('Otrzymaliśmy za mało modeli do uczciwego porównania.')
      }
    } catch (reason) {
      fail(reason)
    }
  }, [demoMode, fail, pollRun, selected])

  const submit = useCallback(async (text: string) => {
    const clean = text.trim()
    if (!clean || busy) return
    lastOperation.current = () => performSubmit(clean, false)
    await performSubmit(clean, true)
  }, [busy, performSubmit])

  const performSelect = useCallback(async (candidate: Candidate, direction: SearchDirection) => {
    setSelected(candidate)
    setError(null)
    setBusy(true)
    try {
      if (demoMode) {
        setRun(demoRunForCandidate(candidate))
        setMessages((current) => [...current, message('assistant', `Porównałam trzy przygotowane oferty dla ${candidate.brand} ${candidate.model}.`)])
        setPhase('results')
        setBusy(false)
        return
      }
      if (!sessionId.current) throw new Error('Sesja wygasła. Zacznij od ponownego wysłania potrzeby.')
      const response = await selectProduct(sessionId.current, candidate.product_id, direction)
      await pollRun(response.run_id)
    } catch (reason) {
      fail(reason)
    }
  }, [demoMode, fail, pollRun])

  const choose = useCallback(async (candidate: Candidate, direction: SearchDirection) => {
    lastOperation.current = () => performSelect(candidate, direction)
    await performSelect(candidate, direction)
  }, [performSelect])

  const retry = useCallback(async () => {
    if (lastOperation.current && !busy) await lastOperation.current()
  }, [busy])

  const useDemo = useCallback(() => {
    activeRequest.current += 1
    setDemoMode(true)
    setError(null)
    setBusy(false)
    setCandidates(demoCandidates)
    setSelected(null)
    setRun(null)
    setMessages((current) => [...current, message('assistant', 'Uruchomiłam przygotowany scenariusz. Wybierz jeden z czterech modeli; dane są oznaczone jako demonstracyjne.')])
    setPhase('selecting')
  }, [])

  const reset = useCallback(() => {
    activeRequest.current += 1
    sessionId.current = null
    lastOperation.current = null
    setPhase('idle')
    setMessages([])
    setCandidates([])
    setSelected(null)
    setRun(null)
    setError(null)
    setDemoMode(false)
    setBusy(false)
  }, [])

  const restoreHistory = useCallback((history: SessionHistoryResponse) => {
    activeRequest.current += 1
    sessionId.current = history.session.id
    lastOperation.current = null
    setMessages(history.messages.map((item) => ({
      id: item.id,
      role: item.role,
      content: item.content,
    })))
    setCandidates([])
    setSelected(null)
    setRun(null)
    setError(null)
    setDemoMode(false)
    setBusy(false)
    setPhase(history.messages.length ? 'conversing' : 'idle')
  }, [])

  return {
    phase,
    messages,
    candidates,
    selected,
    run,
    recommendations: run?.recommendations ?? [] as Recommendation[],
    error,
    demoMode,
    busy,
    submit,
    choose,
    retry,
    useDemo,
    reset,
    restoreHistory,
  }
}
