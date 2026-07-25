import { useEffect, useState, type FormEvent } from 'react'
import { apiGet, apiPostJson } from '../lib/api'

type TailorResult = {
  id: number
  content_md: string
  mode: string
}

type Job = {
  id: number
  title: string
  company: string | null
  description: string
}

export function TailorPage() {
  const queryJobId = Number(new URLSearchParams(window.location.search).get('jobId')) || undefined
  const [title, setTitle] = useState('')
  const [company, setCompany] = useState('')
  const [jd, setJd] = useState('')
  const [jobId] = useState<number | undefined>(queryJobId)
  const [result, setResult] = useState<TailorResult | null>(null)
  const [edited, setEdited] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!jobId) return
    apiGet<Job>(`/api/jobs/${jobId}`)
      .then((job) => {
        setJd(job.description)
        setTitle(job.title)
        setCompany(job.company || '')
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)))
  }, [jobId])

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const data = await apiPostJson<TailorResult>('/api/tailor', {
        job_description: jd,
        title: title || null,
        company: company || null,
        job_id: jobId ?? null,
        run_crew: false,
      })
      setResult(data)
      setEdited(data.content_md)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page stack">
      <div>
        <h1>Tailor CV</h1>
        <p className="lede">
          Paste a job description. We adapt your <strong>baseline resume</strong> and
          Memory — title and company are optional.
        </p>
      </div>
      <form className="stack" onSubmit={onSubmit}>
        <div className="field">
          <label htmlFor="t-jd">Job description (required)</label>
          <textarea
            id="t-jd"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            required
            minLength={20}
          />
        </div>
        <div className="field">
          <label htmlFor="t-title">Role title (optional)</label>
          <input id="t-title" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="t-company">Company (optional)</label>
          <input id="t-company" value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
        <button type="submit" disabled={busy}>
          {busy ? 'Working…' : 'Generate'}
        </button>
      </form>
      {error && <div className="status">{error}</div>}
      {result && (
        <div className="stack">
          <p className="muted">Variant #{result.id} · grounded in your baseline CV</p>
          <div className="field">
            <label htmlFor="cv">Editable CV</label>
            <textarea
              id="cv"
              value={edited}
              onChange={(e) => setEdited(e.target.value)}
              style={{ minHeight: '18rem' }}
            />
          </div>
          <a className="button" href={`/api/tailor/${result.id}/docx`}>
            Download DOCX
          </a>
        </div>
      )}
    </div>
  )
}
