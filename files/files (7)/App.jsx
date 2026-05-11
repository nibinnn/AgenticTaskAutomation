import { useState } from 'react'
import { AuthProvider, useAuth } from './lib/auth'
import Login from './pages/Login'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import AgentPage from './pages/AgentPage'
import QueriesPage from './pages/QueriesPage'

function AppShell() {
  const { user } = useAuth()
  const [page, setPage] = useState('dashboard')
  const [pendingQuery, setPendingQuery] = useState(null)

  if (!user) return <Login />

  function handleRunSavedQuery(query) {
    setPendingQuery(query)
    setPage('agent')
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar active={page} setActive={setPage} />
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex items-center justify-between px-6 py-3.5 border-b border-ink-800 bg-ink-900/60 backdrop-blur-sm shrink-0">
          <div className="font-display font-semibold text-ink-100 text-sm capitalize">
            {page === 'agent' ? 'AI Agent' : page === 'queries' ? 'Saved Queries' : 'Dashboard'}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-xs text-ink-600">
              <div className="w-1.5 h-1.5 rounded-full bg-lime animate-pulse" />
              API connected
            </div>
          </div>
        </header>

        {/* Page content */}
        {page === 'dashboard' && <Dashboard />}
        {page === 'agent' && (
          <AgentPage
            initialQuery={pendingQuery}
            onQueryConsumed={() => setPendingQuery(null)}
          />
        )}
        {page === 'queries' && (
          <QueriesPage onRunQuery={handleRunSavedQuery} />
        )}
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppShell />
    </AuthProvider>
  )
}
