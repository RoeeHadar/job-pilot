import type { ReactNode } from 'react'
import './App.css'
import { RequireOnboarding } from './components/RequireOnboarding'
import { AlertsPage } from './pages/AlertsPage'
import { HomePage } from './pages/HomePage'
import { JobsPage } from './pages/JobsPage'
import { OnboardingPage } from './pages/OnboardingPage'
import { TailorPage } from './pages/TailorPage'

function App() {
  const path = window.location.pathname
  const guarded = (page: ReactNode) => (
    <RequireOnboarding>{page}</RequireOnboarding>
  )
  const page =
    path === '/onboarding' ? (
      <OnboardingPage />
    ) : path === '/jobs' ? (
      guarded(<JobsPage />)
    ) : path === '/tailor' ? (
      guarded(<TailorPage />)
    ) : path === '/alerts' ? (
      guarded(<AlertsPage />)
    ) : (
      <HomePage />
    )

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden />
          <div>
            <p className="brand-name">Job Pilot</p>
            <p className="brand-sub">Israel · local-first</p>
          </div>
        </div>
        <nav className="nav">
          {[
            ['/', 'Home'],
            ['/onboarding', 'Setup'],
            ['/jobs', 'Jobs'],
            ['/tailor', 'Tailor CV'],
            ['/alerts', 'Alerts'],
          ].map(([href, label]) => (
            <a key={href} href={href} className={path === href ? 'active' : ''}>
              {label}
            </a>
          ))}
        </nav>
      </header>
      <main className="main">{page}</main>
    </div>
  )
}

export default App
