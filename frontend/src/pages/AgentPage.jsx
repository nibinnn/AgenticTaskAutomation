import { useState, useRef } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useSavedQueries } from '../hooks/useSavedQueries'

const SUGGESTIONS = [
  'Analyze the sales data, find top revenue products, and summarize the key insights',
  'Filter products with revenue above $3000, convert to CSV, and save as report.csv',
  'Classify all customer feedback by sentiment and generate an executive summary',
  'Compare Widget A and Widget B performance across all regions',
  'Generate a 90-day sales growth plan based on current revenue trends',
]

const AGENT_COLORS = {
  DataAgent:      { dot: 'bg-emerald-400', badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30' },
  TransformAgent: { dot: 'bg-amber-400',   badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30' },
  FileAgent:      { dot: 'bg-blue-400',    badge: 'bg-blue-500/15 text-blue-300 border-blue-500/30' },
  SchedulerAgent: { dot: 'bg-pink-400',    badge: 'bg-pink-500/15 text-pink-300 border-pink-500/30' },
  AIAgent:        { dot: 'bg-lime',        badge: 'bg-lime/15 text-lime border-lime/30' },
  PlannerAgent:   { dot: 'bg-violet-400',  badge: 'bg-violet-500/15 text-violet-300 border-violet-500/30' },
}

function AgentBadge({ name }) {
  const c = AGENT_COLORS[name] || { badge: 'bg-ink-700 text-ink-300 border-ink-600' }
  return <span className={`tag border text-[11px] ${c.badge}`}>{name}</span>
}

function StepRow({ step, index }) {
  const [expanded, setExpanded] = useState(false)
  const c = AGENT_COLORS[step.agent] || { dot: 'bg-ink-500' }
  const hasOutput = step.output !== null && step.output !== undefined

  return (
    <div className="border border-ink-800 rounded-xl overflow-hidden">
      <button
        onClick={() => hasOutput && setExpanded(v => !v)}
        className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-ink-800/30 transition-colors ${hasOutput ? 'cursor-pointer' : 'cursor-default'}`}
      >
        {/* step number */}
        <div className="w-5 h-5 rounded-full border border-ink-700 flex items-center justify-center text-[10px] text-ink-500 font-mono shrink-0">
          {index + 1}
        </div>
        {/* status dot */}
        <div className={`w-2 h-2 rounded-full shrink-0 ${step.success ? c.dot : 'bg-red-400'}`} />
        {/* name */}
        <span className="flex-1 text-sm font-medium text-ink-100 text-left">{step.name}</span>
        {/* agent badge */}
        <AgentBadge name={step.agent} />
        {/* duration */}
        <span className="text-[11px] font-mono text-ink-500 ml-2">{step.duration.toFixed(2)}s</span>
        {/* expand icon */}
        {hasOutput && (
          <svg className={`w-3.5 h-3.5 text-ink-600 transition-transform ${expanded ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="6 9 12 15 18 9"/></svg>
        )}
      </button>

      {expanded && hasOutput && (
        <div className="px-4 pb-4 pt-1 border-t border-ink-800">
          {step.description && <p className="text-xs text-ink-500 mb-2 italic">{step.description}</p>}
          <pre className="text-xs font-mono text-ink-300 bg-ink-900/60 rounded-lg p-3 overflow-auto max-h-48 whitespace-pre-wrap break-words">
            {typeof step.output === 'object' ? JSON.stringify(step.output, null, 2) : String(step.output)}
          </pre>
          {step.error && <p className="text-xs text-red-400 mt-2">Error: {step.error}</p>}
        </div>
      )}
    </div>
  )
}

function LoadingDots() {
  return (
    <span className="inline-flex items-center gap-1 ml-1">
      {[0, 1, 2].map(i => (
        <span key={i} className="w-1.5 h-1.5 rounded-full bg-lime animate-pulse-dot" style={{ animationDelay: `${i * 0.16}s` }} />
      ))}
    </span>
  )
}

export default function AgentPage({ initialQuery, onQueryConsumed }) {
  const { user } = useAuth()
  const { queries, save, incrementRun } = useSavedQueries(user.id)
  const [instruction, setInstruction] = useState(initialQuery || '')

  // When a saved query is passed in, auto-run it
  useState(() => {
    if (initialQuery) {
      run(initialQuery)
      if (onQueryConsumed) onQueryConsumed()
    }
  }, [initialQuery])
  const [loading, setLoading] = useState(false)
  const [phase, setPhase] = useState('idle') // idle | planning | executing | done | error
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [saveLabel, setSaveLabel] = useState('')
  const [justSaved, setJustSaved] = useState(false)
  const textareaRef = useRef(null)

  const CONTEXT = {
    data: [
      { product: 'Widget A', region: 'North', revenue: 1200, units: 40, quarter: 'Q1' },
      { product: 'Widget B', region: 'South', revenue: 3400, units: 110, quarter: 'Q1' },
      { product: 'Widget A', region: 'South', revenue: 950,  units: 30,  quarter: 'Q2' },
      { product: 'Widget C', region: 'North', revenue: 2100, units: 75,  quarter: 'Q1' },
      { product: 'Widget B', region: 'North', revenue: 4800, units: 160, quarter: 'Q2' },
      { product: 'Widget C', region: 'East',  revenue: 1750, units: 60,  quarter: 'Q2' },
    ],
    feedback: [
      'Onboarding was smooth and the UI is very intuitive!',
      'Terrible support. Waited 3 days, issue unresolved.',
      'Product works as advertised but pricing feels steep.',
      'Amazing! Best purchase I\'ve made this year.',
      'New dashboard feature is confusing.',
      'Fast, reliable, and the team is very responsive.',
    ]
  }

  async function run(query) {
    const q = query || instruction
    if (!q.trim()) return
    setInstruction(q)
    setLoading(true)
    setPhase('planning')
    setResult(null)
    setError('')
    setJustSaved(false)

    try {
      setPhase('executing')
      const res = await api.solve({ requirement: q, context: CONTEXT })
      setResult(res)
      setPhase('done')
    } catch (e) {
      setError(e.message)
      setPhase('error')
    } finally {
      setLoading(false)
    }
  }

  function handleSave() {
    save(instruction, saveLabel || undefined)
    setSaveLabel('')
    setJustSaved(true)
    setTimeout(() => setJustSaved(false), 2000)
  }

  function useSuggestion(s) {
    setInstruction(s)
    textareaRef.current?.focus()
  }

  const successSteps = result?.execution?.filter(s => s.success).length || 0
  const totalSteps   = result?.execution?.length || 0

  return (
    <div className="flex-1 overflow-auto p-6">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Header */}
        <div className="animate-fade-up">
          <h1 className="font-display text-2xl font-bold text-ink-50">AI Agent</h1>
          <p className="text-ink-400 text-sm mt-1">Describe your requirement — the AI designs and executes the pipeline</p>
        </div>

        {/* Instruction box */}
        <div className="card p-5 space-y-4 animate-fade-up" style={{ animationDelay: '0.05s' }}>
          <div>
            <label className="block text-xs font-medium text-ink-500 mb-2 uppercase tracking-widest">Instruction</label>
            <textarea
              ref={textareaRef}
              value={instruction}
              onChange={e => setInstruction(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) run() }}
              placeholder="e.g. Analyze the sales data, find top products by revenue, summarize insights with AI, and save as a CSV report…"
              rows={4}
              className="input-base resize-none leading-relaxed"
            />
            <p className="text-[11px] text-ink-600 mt-1.5">Press <kbd className="font-mono bg-ink-800 border border-ink-700 rounded px-1 py-0.5 text-[10px]">⌘ Enter</kbd> to run</p>
          </div>

          {/* Suggestions */}
          <div>
            <div className="text-[10px] uppercase tracking-widest text-ink-600 mb-2">Quick suggestions</div>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s, i) => (
                <button key={i} onClick={() => useSuggestion(s)}
                  className="text-[11px] text-ink-400 bg-ink-900/60 border border-ink-800 rounded-lg px-2.5 py-1.5 hover:text-lime hover:border-lime/40 transition-all text-left leading-snug max-w-[200px] truncate">
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Actions row */}
          <div className="flex items-center gap-3 pt-1 border-t border-ink-800">
            <button onClick={() => run()} disabled={loading || !instruction.trim()} className="btn-primary flex items-center gap-2">
              {loading ? (
                <><svg className="animate-spin w-3.5 h-3.5" viewBox="0 0 24 24" fill="none"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg> Running…</>
              ) : (
                <><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Run Pipeline</>
              )}
            </button>

            {/* Save query */}
            {instruction.trim() && !loading && (
              <div className="flex items-center gap-2 flex-1">
                <input
                  value={saveLabel}
                  onChange={e => setSaveLabel(e.target.value)}
                  placeholder="Label (optional)"
                  className="input-base py-2 text-xs flex-1"
                />
                <button onClick={handleSave} disabled={justSaved}
                  className="btn-ghost flex items-center gap-1.5 text-xs py-2 px-3 shrink-0">
                  {justSaved ? (
                    <><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg> Saved!</>
                  ) : (
                    <><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg> Save</>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Status / loading */}
        {loading && (
          <div className="card p-5 animate-fade-in">
            <div className="flex items-center gap-3">
              <div className="w-7 h-7 rounded-lg bg-lime/15 flex items-center justify-center">
                <svg className="animate-spin-slow w-4 h-4 text-lime" viewBox="0 0 24 24" fill="none">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <div>
                <div className="text-sm font-medium text-ink-100 flex items-center">
                  {phase === 'planning' ? 'Planning pipeline' : 'Executing steps'}
                  <LoadingDots />
                </div>
                <div className="text-xs text-ink-500 mt-0.5">
                  {phase === 'planning' ? 'AI is designing the optimal workflow…' : 'Running agents in sequence…'}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error */}
        {phase === 'error' && (
          <div className="card border-red-500/30 bg-red-500/5 p-5 animate-fade-in">
            <div className="flex items-start gap-3">
              <div className="w-5 h-5 rounded-full bg-red-500/20 flex items-center justify-center shrink-0 mt-0.5">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </div>
              <div>
                <div className="text-sm font-medium text-red-400">Pipeline failed</div>
                <div className="text-xs text-ink-500 mt-1">{error}</div>
                <p className="text-xs text-ink-600 mt-2">Make sure the backend is running and ANTHROPIC_API_KEY is set.</p>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {result && phase === 'done' && (
          <div className="space-y-4 animate-fade-up">
            {/* Summary banner */}
            <div className="card border-lime/20 bg-lime/5 p-5">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-lime" />
                    <span className="text-xs text-lime font-semibold uppercase tracking-widest">Pipeline Complete</span>
                  </div>
                  <p className="text-sm font-medium text-ink-100">{result.goal_summary}</p>
                  {result.reasoning && <p className="text-xs text-ink-400 mt-1.5 leading-relaxed">{result.reasoning}</p>}
                </div>
                <div className="text-right shrink-0">
                  <div className="text-lg font-display font-bold text-lime">{successSteps}/{totalSteps}</div>
                  <div className="text-[10px] text-ink-500">steps ok</div>
                  <div className="text-[10px] font-mono text-ink-600 mt-0.5">{result.duration?.toFixed(2)}s total</div>
                </div>
              </div>
            </div>

            {/* Generated pipeline steps */}
            <div>
              <div className="text-xs text-ink-500 uppercase tracking-widest mb-3">Execution trace</div>
              <div className="space-y-2">
                {result.execution?.map((step, i) => (
                  <StepRow key={i} step={step} index={i} />
                ))}
              </div>
            </div>

            {/* Final output */}
            {result.final_output !== null && result.final_output !== undefined && (
              <div>
                <div className="text-xs text-ink-500 uppercase tracking-widest mb-2">Final output</div>
                <div className="card p-4">
                  <pre className="text-xs font-mono text-ink-200 overflow-auto max-h-60 whitespace-pre-wrap break-words leading-relaxed">
                    {typeof result.final_output === 'object'
                      ? JSON.stringify(result.final_output, null, 2)
                      : String(result.final_output)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
