import { useEffect, useState, type FormEvent } from 'react'
import { apiGet, apiPostJson } from '../lib/api'

type Job = {
  id: number
  title: string
  company: string | null
  location: string | null
  description: string
  match_score: number | null
  posted_at: string | null
  created_at: string
}

type Feed = {
  mode: 'ranked' | 'newest'
  jobs: Job[]
}

export function JobsPage() {
  const [feed, setFeed] = useState<Feed | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showPaste, setShowPaste] = useState(false)
  const [pasteJd, setPasteJd] = useState('')
  const [busy, setBusy] = useState(false)

  async function refresh() {
    const data = await apiGet<Feed>('/api/jobs/feed')
    setFeed(data)
  }

  useEffect(() => {
    refresh().catch((e) => setError(String(e)))
  }, [])

  async function onPaste(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await apiPostJson('/api/jobs', { description: pasteJd })
      setPasteJd('')
      setShowPaste(false)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page stack">
      <div>
        <h1>Suggested jobs</h1>
        <p className="lede">
          {feed?.mode === 'ranked'
            ? 'Ranked for you from your resume and Memory.'
            : 'Showing recent Israel-market roles (newest first). Personalized ranking unlocks as Memory grows.'}
        </p>
      </div>

      <div className="row">
        <button type="button" className="secondary" onClick={() => refresh()}>
          Refresh
        </button>
        <button type="button" className="secondary" onClick={() => setShowPaste((v) => !v)}>
          {showPaste ? 'Hide paste' : 'Paste a job you found'}
        </button>
      </div>

      {showPaste && (
        <form className="stack" onSubmit={onPaste}>
          <div className="field">
            <label htmlFor="paste-jd">Job description</label>
            <textarea
              id="paste-jd"
              value={pasteJd}
              onChange={(e) => setPasteJd(e.target.value)}
              required
              minLength={20}
              placeholder="Paste the full JD — title/company optional"
            />
          </div>
          <button type="submit" disabled={busy}>
            Add to list
          </button>
        </form>
      )}

      {error && <div className="status">{error}</div>}

      <ul className="list">
        {(feed?.jobs || []).map((job) => (
          <li key={job.id}>
            <strong>
              {job.title}
              {job.company ? ` · ${job.company}` : ''}
            </strong>
            <div className="muted">
              {job.location || 'Israel'}
              {job.match_score != null && feed?.mode === 'ranked'
                ? ` · fit ${Math.round(job.match_score)}`
                : ''}
            </div>
            <p className="muted" style={{ marginTop: '0.4rem' }}>
              {job.description.slice(0, 180)}
              {job.description.length > 180 ? '…' : ''}
            </p>
            <div className="row" style={{ marginTop: '0.6rem' }}>
              <a
                className="button"
                href={`/tailor?jobId=${job.id}`}
              >
                Tailor CV
              </a>
            </div>
          </li>
        ))}
      </ul>

      {feed && feed.jobs.length === 0 && (
        <p className="muted">No jobs yet — paste a JD or connect Apify later.</p>
      )}
    </div>
  )
}
