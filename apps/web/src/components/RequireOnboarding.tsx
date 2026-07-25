import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'
import { getOnboardingStatus, type ProfileStatus } from '../lib/api'

export function RequireOnboarding({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<ProfileStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getOnboardingStatus()
      .then(setStatus)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
  }, [])

  if (error) {
    return <div className="status">{error}</div>
  }
  if (!status) {
    return <p className="muted">Checking profile…</p>
  }
  if (!status.onboarding_complete) {
    window.location.replace('/onboarding')
    return null
  }
  return children
}
