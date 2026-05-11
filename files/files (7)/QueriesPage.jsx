import { useState } from 'react'
import { useAuth } from '../lib/auth'
import { useSavedQueries } from '../hooks/useSavedQueries'

function timeAgo(iso) {
  const diff = Date.now() - new Date(iso).getTime()
  const mins  = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days  = Math.floor(diff / 86400000)
  if (mins < 1)   return 'just now'
  if (mins < 60)  return `${mins}m ago`
  if (hours < 24) return `${hours}h ago`
  return `${days}d ago`
}

export default function QueriesPage({ onRunQuery }) {
  const { user } = useAuth()
  const { queries, remove, update } = useSavedQueries(user.id)
  const [editingId, setEditingId] = useState(null)
  const [editLabel, setEditLabel] = useState('')
  const [search, setSearch] = useState('')

  const filtered = queries.filter(q =>
    q.label.toLowerCase().includes(search.toLowerCase()) ||
    q.query.toLowerCase().includes(search.toLowerCase())
  )

  function startEdit(q) {
    setEditingId(q.id)
    setEditLabel(q.label)
  }

  function commitEdit(id) {
    if (editLabel.trim()) update(id, editLabel.trim())
    setEditingId(null)
  }

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header */}
        <div className="animate-fade-up">
          <h1 className="font-display text-2xl font-bold text-ink-50">Saved Queries</h1>
          <p className="text-ink-400 text-sm mt-1">{queries.length} saved {queries.length === 1 ? 'query' : 'queries'} — click Run to re-execute</p>
        </div>

        {/* Search */}
        {queries.length > 0 && (
          <div className="animate-fade-up" style={{ animationDelay: '0.05s' }}>
            <div className="relative">
              <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              <input
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Search queries…"
                className="input-base pl-10"
              />
            </div>
          </div>
        )}

        {/* Empty state */}
        {queries.length === 0 && (
          <div className="card p-12 text-center animate-fade-up">
            <div className="w-12 h-12 rounded-xl bg-ink-800 flex items-center justify-center mx-auto mb-4">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#55556a" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <div className="text-ink-400 text-sm font-medium mb-1">No saved queries yet</div>
            <div className="text-ink-600 text-xs">Go to AI Agent, run a query, then save it for future use</div>
          </div>
        )}

        {/* Queries list */}
        {filtered.length > 0 && (
          <div className="space-y-3 animate-fade-up" style={{ animationDelay: '0.1s' }}>
            {filtered.map((q, i) => (
              <div key={q.id} className="card-hover p-4 group" style={{ animationDelay: `${i * 0.03}s` }}>
                <div className="flex items-start gap-3">
                  {/* Index */}
                  <div className="w-6 h-6 rounded-lg bg-ink-800 border border-ink-700 flex items-center justify-center text-[10px] font-mono text-ink-500 shrink-0 mt-0.5">
                    {filtered.length - i}
                  </div>

                  <div className="flex-1 min-w-0">
                    {/* Label (editable) */}
                    {editingId === q.id ? (
                      <input
                        autoFocus
                        value={editLabel}
                        onChange={e => setEditLabel(e.target.value)}
                        onBlur={() => commitEdit(q.id)}
                        onKeyDown={e => { if (e.key === 'Enter') commitEdit(q.id); if (e.key === 'Escape') setEditingId(null) }}
                        className="input-base py-1 text-sm font-medium mb-1"
                      />
                    ) : (
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium text-ink-100">{q.label}</span>
                        <button onClick={() => startEdit(q)}
                          className="opacity-0 group-hover:opacity-100 text-ink-600 hover:text-ink-400 transition-all">
                          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                          </svg>
                        </button>
                      </div>
                    )}

                    {/* Query preview */}
                    <p className="text-xs text-ink-500 leading-relaxed line-clamp-2">{q.query}</p>

                    {/* Meta */}
                    <div className="flex items-center gap-3 mt-2">
                      <span className="text-[10px] font-mono text-ink-600">{timeAgo(q.createdAt)}</span>
                      {q.runCount > 0 && (
                        <span className="text-[10px] text-ink-600">· run {q.runCount}×</span>
                      )}
                      {q.lastRun && (
                        <span className="text-[10px] text-ink-600">· last {timeAgo(q.lastRun)}</span>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button
                      onClick={() => onRunQuery(q.query)}
                      className="flex items-center gap-1.5 text-xs font-medium text-lime bg-lime/10 border border-lime/25 rounded-lg px-2.5 py-1.5 hover:bg-lime/20 transition-colors">
                      <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                      Run
                    </button>
                    <button
                      onClick={() => remove(q.id)}
                      className="text-ink-600 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10 transition-colors">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* No search results */}
        {queries.length > 0 && filtered.length === 0 && (
          <div className="card p-8 text-center">
            <div className="text-ink-500 text-sm">No queries match "<span className="text-ink-300">{search}</span>"</div>
          </div>
        )}
      </div>
    </div>
  )
}
