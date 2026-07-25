import { useEffect, useState } from 'react'
import { apiGet, apiPostJson } from '../lib/api'

type Alert = {
  id: number
  kind: string
  title: string
  body: string
  read: boolean
}

export function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [error, setError] = useState<string | null>(null)

  async function refresh() {
    const data = await apiGet<Alert[]>('/api/alerts')
    setAlerts(data)
  }

  useEffect(() => {
    refresh().catch((e) => setError(String(e)))
  }, [])

  async function addDemo() {
    await apiPostJson('/api/alerts/demo', {})
    await refresh()
  }

  async function markRead(id: number) {
    await apiPostJson(`/api/alerts/${id}/read`, {})
    await refresh()
  }

  return (
    <div className="page stack">
      <div>
        <h1>Alerts</h1>
        <p className="lede">
          MVP inbox for matched job-board postings while the local app runs.
          LinkedIn hiring-signal alerts come in phase 2.
        </p>
      </div>
      <div className="row">
        <button type="button" onClick={addDemo}>
          Add demo alert
        </button>
        <button type="button" className="secondary" onClick={() => refresh()}>
          Refresh
        </button>
      </div>
      {error && <div className="status">{error}</div>}
      <ul className="list">
        {alerts.map((a) => (
          <li key={a.id}>
            <strong>
              {a.title}
              {a.read ? '' : ' · new'}
            </strong>
            <div className="muted">{a.body}</div>
            {!a.read && (
              <button type="button" className="secondary" onClick={() => markRead(a.id)}>
                Mark read
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
