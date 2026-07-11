import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createSession, getRun, listHistory, setAccessTokenProvider } from './client'

describe('api client', () => {
  afterEach(() => {
    setAccessTokenProvider(async () => null)
    vi.unstubAllGlobals()
    vi.useRealTimers()
  })

  it('parses a successful response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ session_id: 'one', stage: 'discovery' }), { status: 201 })))
    await expect(createSession()).resolves.toEqual({ session_id: 'one', stage: 'discovery' })
  })

  it('turns backend details into a readable error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: { message: 'Usługi są niedostępne' } }), { status: 503 })))
    await expect(createSession()).rejects.toEqual(new ApiError('Usługi są niedostępne', 503))
  })

  it('attaches the current access token to authenticated requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ sessions: [] }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    setAccessTokenProvider(async () => 'verified-token')

    await listHistory()

    expect(fetchMock).toHaveBeenCalledWith('/api/sessions/history', expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer verified-token' }),
    }))
  })

  it('keeps guest requests free of an authorization header', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ session_id: 'guest', stage: 'discovery' }), { status: 201 }))
    vi.stubGlobal('fetch', fetchMock)

    await createSession()

    const headers = fetchMock.mock.calls[0][1].headers as Record<string, string>
    expect(headers.Authorization).toBeUndefined()
  })

  it('stops a hung run poll instead of leaving the search screen active forever', async () => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn(() => new Promise<Response>(() => {})))

    const outcome = expect(getRun('stuck-run')).rejects.toEqual(
      new ApiError('Połączenie z serwerem trwa zbyt długo. Spróbuj ponownie.', 408),
    )
    await vi.advanceTimersByTimeAsync(20_000)

    await outcome
  })
})
