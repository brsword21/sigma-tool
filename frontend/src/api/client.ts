import type { HistoryListResponse, MessageResponse, RunResponse, SearchDirection, SessionHistoryResponse, SessionResponse } from './types'

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message)
    this.name = 'ApiError'
  }
}

type AccessTokenProvider = () => Promise<string | null>

let accessTokenProvider: AccessTokenProvider = async () => null

export function setAccessTokenProvider(provider: AccessTokenProvider) {
  accessTokenProvider = provider
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    const accessToken = await accessTokenProvider()
    response = await fetch(`/api${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        ...init?.headers,
      },
    })
  } catch {
    throw new ApiError('Nie udało się połączyć z backendem Picky.', 0)
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

export const sendMessage = (sessionId: string, message: string) =>
  request<MessageResponse>(`/sessions/${sessionId}/messages`, {
    method: 'POST',
    body: JSON.stringify({ message }),
  })

export const selectProduct = (sessionId: string, productId: string, direction: SearchDirection) =>
  request<{ run_id: string; status: RunResponse['status'] }>(
    `/sessions/${sessionId}/products/${productId}/select`,
    { method: 'POST', body: JSON.stringify({ direction }) },
  )

export const getRun = (runId: string) => request<RunResponse>(`/runs/${runId}`)

export const refreshRun = (runId: string) =>
  request<{ run_id: string; status: RunResponse['status'] }>(`/runs/${runId}/refresh`, { method: 'POST' })

export const listHistory = () => request<HistoryListResponse>('/sessions/history')

export const getSessionHistory = (sessionId: string) =>
  request<SessionHistoryResponse>(`/sessions/${sessionId}/history`)
