import { useEffect, useState, type FormEvent } from 'react'
import { apiGet, apiPostJson } from '../lib/api'

type RubricDim = {
  id: string
  label: string
  score: number
  citation: string
}

type Job = {
  id: number
  title: string
  company: string | null
  location: string | null
  description: string
  match_score: number | null
  posted_at: string | null
  created_at: string
  keyword_gaps?: string[]
  rubric?: RubricDim[] | null
  rubric_mode?: string | null
  advisory?: Record<string, string> | null
  feedback?: string | null
  status?: string
}

type Feed = {
  mode: 'ranked' | 'newest'
  llm_available?: boolean
  jobs: Job[]
}

type OutreachPack = {
  job_id: number
  short_pitch: string
  linkedin_note: string
  cold_email_subject: string
  cold_email_body: string
  disclaimer: string
}

export function JobsPage() {
  const [feed, setFeed] = useState<Feed | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [showPaste, setShowPaste] = useState(false)
  const [pasteJd, setPasteJd] = useState('')
  const [busy, setBusy] = useState(false)
  const [expanded, setExpanded] = useState<number | null>(null)
  const [outreach, setOutreach] = useState<OutreachPack | null>(null)

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

  async function sendFeedback(jobId: number, action: string, snoozeDays?: number) {
    setError(null)
    try {
      await apiPostJson(`/api/jobs/${jobId}/feedback`, {
        action,
        snooze_days: snoozeDays ?? 5,
      })
      if (outreach?.job_id === jobId) setOutreach(null)
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function setStatus(jobId: number, status: string) {
    setError(null)
    try {
      await apiPostJson(`/api/jobs/${jobId}/status`, { status })
      await refresh()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  async function loadOutreach(jobId: number) {
    setError(null)
    try {
      const pack = await apiPostJson<OutreachPack>(`/api/jobs/${jobId}/outreach-pack`, {})
      setOutreach(pack)
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
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
              {` · ${job.status || 'saved'}`}
              {job.feedback === 'like' ? ' · liked' : ''}
            </div>
            <p className="muted" style={{ marginTop: '0.4rem' }}>
              {job.description.slice(0, 180)}
              {job.description.length > 180 ? '…' : ''}
            </p>
            {feed?.mode === 'ranked' && (job.keyword_gaps?.length || job.rubric?.length) ? (
              <div className="fit-panel">
                {job.keyword_gaps && job.keyword_gaps.length > 0 && (
                  <p className="muted gaps">
                    <span className="gaps-label">Keyword gaps: </span>
                    {job.keyword_gaps.join(', ')}
                  </p>
                )}
                <button
                  type="button"
                  className="secondary"
                  onClick={() => setExpanded((id) => (id === job.id ? null : job.id))}
                >
                  {expanded === job.id ? 'Hide fit rubric' : 'Fit rubric'}
                </button>
                {expanded === job.id && job.rubric && (
                  <ul className="rubric">
                    {job.rubric.map((dim) => (
                      <li key={dim.id}>
                        <strong>
                          {dim.label}: {Math.round(dim.score)}
                        </strong>
                        <div className="muted">{dim.citation}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : null}
            <div className="row" style={{ marginTop: '0.6rem' }}>
              <a className="button" href={`/tailor?jobId=${job.id}`}>
                Tailor CV
              </a>
              <button type="button" className="secondary" onClick={() => loadOutreach(job.id)}>
                Outreach pack
              </button>
              <button type="button" className="secondary" onClick={() => sendFeedback(job.id, 'like')}>
                Like
              </button>
              <button type="button" className="secondary" onClick={() => sendFeedback(job.id, 'dislike')}>
                Dislike
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() => sendFeedback(job.id, 'snooze', 5)}
              >
                Snooze 5d
              </button>
              <button type="button" className="secondary" onClick={() => sendFeedback(job.id, 'dismiss')}>
                Dismiss
              </button>
              {job.status !== 'ready' && (
                <button type="button" className="secondary" onClick={() => setStatus(job.id, 'ready')}>
                  Mark ready
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      {outreach && (
        <div className="stack outreach-pack">
          <h2>Outreach pack</h2>
          <p className="muted">{outreach.disclaimer}</p>
          <div className="field">
            <label>Short pitch</label>
            <textarea readOnly value={outreach.short_pitch} rows={3} />
          </div>
          <div className="field">
            <label>LinkedIn note</label>
            <textarea readOnly value={outreach.linkedin_note} rows={3} />
          </div>
          <div className="field">
            <label>Cold email subject</label>
            <input readOnly value={outreach.cold_email_subject} />
          </div>
          <div className="field">
            <label>Cold email body</label>
            <textarea readOnly value={outreach.cold_email_body} rows={8} />
          </div>
          <button type="button" className="secondary" onClick={() => setOutreach(null)}>
            Close pack
          </button>
        </div>
      )}

      {feed && feed.jobs.length === 0 && (
        <p className="muted">No jobs yet — paste a JD or connect Apify later.</p>
      )}
    </div>
  )
}
