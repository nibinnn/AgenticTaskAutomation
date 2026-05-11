import { useState } from 'react'
import { useAuth } from '../lib/auth'

export default function Login() {
  const { login, error, setError } = useAuth()
  const [email, setEmail] = useState('arjun@acme.io')
  const [password, setPassword] = useState('demo123')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    await new Promise(r => setTimeout(r, 600))
    login(email, password)
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] rounded-full"
          style={{ background: 'radial-gradient(circle, rgba(200,241,53,0.05) 0%, transparent 70%)' }} />
      </div>

      <div className="w-full max-w-sm animate-fade-up">
        {/* Logo */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center gap-2 mb-6">
            <div className="w-9 h-9 rounded-xl bg-lime flex items-center justify-center">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#0D0D0F" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="font-display font-700 text-xl tracking-tight text-ink-100">AgentOS</span>
          </div>
          <h1 className="font-display text-3xl font-bold text-ink-50 mb-2">Welcome back</h1>
          <p className="text-ink-400 text-sm">Sign in to your intelligence dashboard</p>
        </div>

        {/* Demo credentials hint */}
        <div className="card mb-6 p-3 flex items-start gap-3">
          <div className="w-4 h-4 rounded-full bg-lime/20 flex items-center justify-center mt-0.5 shrink-0">
            <div className="w-1.5 h-1.5 rounded-full bg-lime" />
          </div>
          <div className="text-xs text-ink-400 leading-relaxed">
            Demo — <span className="text-ink-200">arjun@acme.io</span> or <span className="text-ink-200">priya@acme.io</span>, password: <span className="font-mono text-lime">demo123</span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="block text-xs font-medium text-ink-400 mb-1.5">Email address</label>
            <input
              type="email"
              value={email}
              onChange={e => { setEmail(e.target.value); setError('') }}
              className="input-base"
              placeholder="you@acme.io"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-ink-400 mb-1.5">Password</label>
            <input
              type="password"
              value={password}
              onChange={e => { setPassword(e.target.value); setError('') }}
              className="input-base"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <p className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                Signing in…
              </span>
            ) : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
