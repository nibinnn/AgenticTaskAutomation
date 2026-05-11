import { useAuth } from '../lib/auth'

const NAV = [
  { id: 'dashboard', label: 'Dashboard', icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg> },
  { id: 'agent',     label: 'AI Agent',   icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a2 2 0 012 2v2a2 2 0 01-2 2 2 2 0 01-2-2V4a2 2 0 012-2z"/><path d="M12 8v4M8 12H4a2 2 0 00-2 2v4a2 2 0 002 2h16a2 2 0 002-2v-4a2 2 0 00-2-2h-4"/><circle cx="8" cy="18" r="1"/><circle cx="16" cy="18" r="1"/></svg> },
  { id: 'queries',   label: 'Saved Queries', icon: <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg> },
]

export default function Sidebar({ active, setActive }) {
  const { user, logout } = useAuth()

  return (
    <aside className="w-60 shrink-0 flex flex-col border-r border-ink-800 bg-ink-900/80 backdrop-blur-xl">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-ink-800">
        <div className="w-8 h-8 rounded-lg bg-lime flex items-center justify-center shrink-0">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#0D0D0F" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <div>
          <div className="font-display font-bold text-sm text-ink-50 leading-none">AgentOS</div>
          <div className="text-[10px] text-ink-500 mt-0.5 font-mono">v2.0</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        <div className="text-[10px] font-semibold uppercase tracking-widest text-ink-600 px-3 mb-2">Navigation</div>
        {NAV.map(item => (
          <button
            key={item.id}
            onClick={() => setActive(item.id)}
            className={`sidebar-link w-full ${active === item.id ? 'active' : ''}`}
          >
            <span className={active === item.id ? 'text-lime' : ''}>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* User */}
      <div className="px-3 py-4 border-t border-ink-800">
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl">
          <div className="w-8 h-8 rounded-lg bg-lime/20 border border-lime/30 flex items-center justify-center text-xs font-bold text-lime font-mono shrink-0">
            {user?.avatar}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-ink-100 truncate">{user?.name}</div>
            <div className="text-[10px] text-ink-500 truncate">{user?.role}</div>
          </div>
          <button onClick={logout} title="Sign out"
            className="text-ink-600 hover:text-red-400 transition-colors">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  )
}
