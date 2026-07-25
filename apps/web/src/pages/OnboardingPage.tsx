import { useEffect, useState, type FormEvent } from 'react'
import {
  apiPostJson,
  apiPutJson,
  apiUpload,
  getOnboardingStatus,
  type ProfileStatus,
} from '../lib/api'

type UploadOut = {
  ok: boolean
  filename: string
  extraction_quality: string
  needs_review: boolean
  message: string
}

type Step = 'details' | 'resume' | 'review' | 'done'

export function OnboardingPage() {
  const [step, setStep] = useState<Step>('details')
  const [name, setName] = useState('')
  const [title, setTitle] = useState('')
  const [skills, setSkills] = useState('')
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState<ProfileStatus | null>(null)

  useEffect(() => {
    getOnboardingStatus()
      .then((s) => {
        setStatus(s)
        setName(s.name || '')
        setTitle(s.title || '')
        setSkills(s.skills_notes || '')
        if (s.onboarding_complete) {
          setStep('done')
        } else if (s.has_baseline_resume && s.name && s.title) {
          setStep(s.extraction_quality === 'low' ? 'review' : 'done')
        } else if (s.name && s.title) {
          setStep('resume')
        }
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false))
  }, [])

  async function saveDetails(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const s = await apiPutJson<ProfileStatus>('/api/onboarding/profile', {
        name,
        title,
        skills_notes: skills,
      })
      setStatus(s)
      setStep('resume')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  async function onFile(file: File | null) {
    if (!file) return
    setBusy(true)
    setError(null)
    setMessage(null)
    try {
      const data = await apiUpload<UploadOut>('/api/onboarding/resume', file)
      setMessage(data.message)
      const s = await getOnboardingStatus()
      setStatus(s)
      setStep(data.needs_review ? 'review' : 'done')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  async function saveReview(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await apiPutJson('/api/onboarding/profile', {
        name,
        title,
        skills_notes: skills,
      })
      setStep('done')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  async function finish() {
    setBusy(true)
    setError(null)
    try {
      await apiPostJson('/api/onboarding/complete', {})
      window.location.assign('/jobs')
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  if (loading) return <p className="muted">Loading local profile…</p>

  return (
    <div className="page stack">
      <div>
        <h1>Get started</h1>
        <p className="lede">
          Set up your local profile once. We prepare Memory from your resume —
          then Jobs and Tailor unlock.
        </p>
      </div>

      {step === 'details' && (
        <form className="stack" onSubmit={saveDetails}>
          <div className="field">
            <label htmlFor="name">Full name</label>
            <input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="title">Current title</label>
            <input
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Backend Engineer"
              required
            />
          </div>
          <div className="field">
            <label htmlFor="skills">Skills notes (optional)</label>
            <textarea id="skills" value={skills} onChange={(e) => setSkills(e.target.value)} />
          </div>
          <button type="submit" disabled={busy}>
            Continue
          </button>
        </form>
      )}

      {step === 'resume' && (
        <div className="stack">
          <p className="muted">
            Hi {name}. Upload your baseline resume (PDF preferred).
          </p>
          <div className="field">
            <label htmlFor="resume">Resume file</label>
            <input
              id="resume"
              type="file"
              accept=".pdf,.docx,.txt,.md,.rtf,.odt,application/pdf"
              disabled={busy}
              onChange={(e) => onFile(e.target.files?.[0] ?? null)}
            />
          </div>
          {busy && <p className="muted">Loading resume…</p>}
          {message && <div className="status success">{message}</div>}
        </div>
      )}

      {step === 'review' && (
        <form className="stack" onSubmit={saveReview}>
          <div className="status">
            Resume loaded, but extraction looked weak. Confirm your details —
            we won&apos;t show the raw file text.
          </div>
          <div className="field">
            <label htmlFor="r-name">Full name</label>
            <input id="r-name" value={name} onChange={(e) => setName(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="r-title">Current title</label>
            <input id="r-title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="r-skills">Skills / corrections</label>
            <textarea id="r-skills" value={skills} onChange={(e) => setSkills(e.target.value)} />
          </div>
          <button type="submit" disabled={busy}>
            Continue
          </button>
        </form>
      )}

      {step === 'done' && (
        <div className="stack">
          <div className="status success">
            {message ||
              (status?.resume_filename
                ? `Resume loaded: ${status.resume_filename}`
                : 'Profile ready.')}
          </div>
          <p className="muted">
            Memory is prepared from your baseline CV. Continue to see suggested
            jobs.
          </p>
          <button type="button" disabled={busy} onClick={finish}>
            {status?.onboarding_complete ? 'Go to Jobs' : 'Finish setup'}
          </button>
        </div>
      )}

      {error && <div className="status">{error}</div>}
    </div>
  )
}
