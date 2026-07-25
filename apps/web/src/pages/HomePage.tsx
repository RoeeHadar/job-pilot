import { useEffect, useState } from 'react'
import { getOnboardingStatus, type ProfileStatus } from '../lib/api'

export function HomePage() {
  const [status, setStatus] = useState<ProfileStatus | null>(null)

  useEffect(() => {
    getOnboardingStatus()
      .then(setStatus)
      .catch(() => setStatus(null))
  }, [])

  const ready = status?.onboarding_complete

  return (
    <div className="page">
      <h1>Job Pilot</h1>
      <p className="lede">
        Local-first matching for Israeli developers. Complete setup once, then
        get suggested fits and tailor your CV from any job description.
      </p>
      <div className="row">
        {!ready ? (
          <a className="button" href="/onboarding">
            Start setup
          </a>
        ) : (
          <>
            <a className="button" href="/jobs">
              Suggested jobs
            </a>
            <a className="button secondary" href="/tailor">
              Tailor a CV
            </a>
          </>
        )}
      </div>
      {ready && status && (
        <p className="muted" style={{ marginTop: '1.25rem' }}>
          Signed in locally as {status.name} · {status.title}
        </p>
      )}
    </div>
  )
}
