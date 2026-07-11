import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createSession } from './client'

describe('api client', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('parses a successful response', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ session_id: 'one', stage: 'discovery' }), { status: 201 })))
    await expect(createSession()).resolves.toEqual({ session_id: 'one', stage: 'discovery' })
  })

  it('turns backend details into a readable error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: { message: 'Usługi są niedostępne' } }), { status: 503 })))
    await expect(createSession()).rejects.toEqual(new ApiError('Usługi są niedostępne', 503))
  })
})
