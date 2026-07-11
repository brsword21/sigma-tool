import type { User } from '@supabase/supabase-js'
import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { setAccessTokenProvider } from '../api/client'
import { authConfigured, supabase } from './supabase'

type AuthStatus = 'loading' | 'signed-out' | 'signed-in'

interface AuthContextValue {
  configured: boolean
  status: AuthStatus
  user: User | null
  signInWithMagicLink: (email: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>(authConfigured ? 'loading' : 'signed-out')
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    let active = true
    setAccessTokenProvider(async () => {
      if (!supabase) return null
      const { data } = await supabase.auth.getSession()
      return data.session?.access_token ?? null
    })
    if (!supabase) return () => setAccessTokenProvider(async () => null)

    void supabase.auth.getSession().then(({ data }) => {
      if (!active) return
      setUser(data.session?.user ?? null)
      setStatus(data.session ? 'signed-in' : 'signed-out')
    })
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!active) return
      setUser(session?.user ?? null)
      setStatus(session ? 'signed-in' : 'signed-out')
    })
    return () => {
      active = false
      listener.subscription.unsubscribe()
      setAccessTokenProvider(async () => null)
    }
  }, [])

  const value = useMemo<AuthContextValue>(() => ({
    configured: authConfigured,
    status,
    user,
    signInWithMagicLink: async (email: string) => {
      if (!supabase) throw new Error('Logowanie nie jest jeszcze skonfigurowane.')
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: { emailRedirectTo: window.location.origin },
      })
      if (error) throw new Error('Nie udało się wysłać linku. Sprawdź adres i spróbuj ponownie.')
    },
    signOut: async () => {
      if (!supabase) return
      const { error } = await supabase.auth.signOut()
      if (error) throw new Error('Nie udało się wylogować. Spróbuj ponownie.')
    },
  }), [status, user])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('useAuth must be used inside AuthProvider')
  return value
}
