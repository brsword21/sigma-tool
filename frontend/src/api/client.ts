import type { HistoryListResponse, MessageResponse, RunResponse, SearchDirection, SessionHistoryResponse, SessionResponse } from './types'

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

type AccessTokenProvider = () => Promise<string | null>

let accessTokenProvider: AccessTokenProvider = async () => null

const DEFAULT_REQUEST_TIMEOUT_MS = 20_000
const RUN_POLL_REQUEST_TIMEOUT_MS = 20_000
const TIMEOUT_MESSAGE = 'Połączenie z serwerem trwa zbyt długo. Spróbuj ponownie.'

export function setAccessTokenProvider(provider: AccessTokenProvider) {
  accessTokenProvider = provider
}

async function request<T>(
  path: string,
  init?: RequestInit,
  timeoutMs = DEFAULT_REQUEST_TIMEOUT_MS,
): Promise<T> {
  let response: Response
  let timeout: ReturnType<typeof globalThis.setTimeout> | undefined
  const controller = new AbortController()
  try {
    const requestPromise = (async () => {
      const accessToken = await accessTokenProvider()
      return fetch(`/api${path}`, {
        ...init,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
          ...init?.headers,
        },
      })
    })()
    const timeoutPromise = new Promise<never>((_, reject) => {
      timeout = globalThis.setTimeout(() => {
        controller.abort()
        reject(new ApiError(TIMEOUT_MESSAGE, 408))
      }, timeoutMs)
    })
    response = await Promise.race([requestPromise, timeoutPromise])
  } catch (reason) {
    if (reason instanceof ApiError) throw reason
    throw new ApiError('Nie udało się połączyć z backendem Picky.', 0)
  } finally {
    if (timeout !== undefined) globalThis.clearTimeout(timeout)
  }
  if (!response.ok) {
    let message = response.status >= 500
      ? 'Backend nie mógł obsłużyć żądania.'
      : 'Żądanie nie zostało przyjęte.'
    try {
      const body = await response.json() as { detail?: string | { message?: string; code?: string }; error?: { message?: string } }
      if (typeof body.detail === 'string') message = body.detail
      else message = body.detail?.message ?? body.error?.message ?? message
      if (body.detail && typeof body.detail !== 'string' && !body.detail.message && body.detail.code) {
        message = body.detail.code.replaceAll('_', ' ')
      }
    } catch {
      // The readable default above is safer than exposing an HTML proxy error.
    }
    throw new ApiError(message, response.status)
  }
  return response.json() as Promise<T>
}

export const createSession = () => request<SessionResponse>('/sessions', { method: 'POST' })

// Discovery runs the LLM plus a live market probe per suggestion, so it needs
// far more headroom than regular requests.
const DISCOVERY_REQUEST_TIMEOUT_MS = 60_000

export const sendMessage = (sessionId: string, message: string) =>
  request<MessageResponse>(`/sessions/${sessionId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  }, DISCOVERY_REQUEST_TIMEOUT_MS)

export const selectProduct = (sessionId: string, productId: string, direction: SearchDirection) =>
  request<{ run_id: string; status: RunResponse['status'] }>(
    `/sessions/${sessionId}/products/${productId}/select`,
    { method: 'POST', body: JSON.stringify({ direction }) },
  )

export const getRun = (runId: string) =>
  request<RunResponse>(`/runs/${runId}`, undefined, RUN_POLL_REQUEST_TIMEOUT_MS)

export const refreshRun = (runId: string) =>
  request<{ run_id: string; status: RunResponse['status'] }>(`/runs/${runId}/refresh`, { method: 'POST' })

export const listHistory = () => request<HistoryListResponse>('/sessions/history')

export const getSessionHistory = (sessionId: string) =>
  request<SessionHistoryResponse>(`/sessions/${sessionId}/history`)
