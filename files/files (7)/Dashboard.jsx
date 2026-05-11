import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'

const SALES = [
  { product: 'Widget A', revenue: 3150, units: 92, region: 'North' },
  { product: 'Widget B', revenue: 8200, units: 270, region: 'South' },
  { product: 'Widget C', revenue: 3850, units: 135, region: 'North' },
  { product: 'Widget D', revenue: 5400, units: 180, region: 'East' },
  { product: 'Widget E', revenue: 2100, units: 70, region: 'West' },
]

const MONTHLY = [
  { month: 'Jan', revenue: 18400 }, { month: 'Feb', revenue: 21200 },
  { month: 'Mar', revenue: 19800 }, { month: 'Apr', revenue: 24500 },
  { month: 'May', revenue: 22100 }, { month: 'Jun', revenue: 27300 },
]

const SENTIMENT = [
  { name: 'Positive', value: 58, color: '#C8F135' },
  { name: 'Neutral',  value: 24, color: '#6B7A9F' },
  { name: 'Negative', value: 18, color: '#ff6b6b' },
]

const FEEDBACK = [
  { id: 1, text: 'Onboarding was smooth and the UI is very intuitive!', sentiment: 'positive', score: 0.92, date: '2024-06-10' },
  { id: 2, text: 'Terrible support. Waited 3 days and issue still unresolved.', sentiment: 'negative', score: 0.12, date: '2024-06-09' },
  { id: 3, text: 'Product works as advertised but pricing feels steep.', sentiment: 'neutral', score: 0.51, date: '2024-06-09' },
  { id: 4, text: 'Amazing! Best purchase I\'ve made this year. 5 stars!', sentiment: 'positive', score: 0.97, date: '2024-06-08' },
  { id: 5, text: 'New dashboard feature is confusing. Hard to find export.', sentiment: 'negative', score: 0.22, date: '2024-06-08' },
  { id: 6, text: 'Fast, reliable, and the team is very responsive.', sentiment: 'positive', score: 0.89, date: '2024-06-07' },
]

const TOOLTIP_STYLE = {
  contentStyle: { background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12, fontSize: 12 },
  labelStyle: { color: '#a8a8b0' },
  itemStyle: { color: '#e8e8ea' },
}

function StatCard({ label, value, sub, accent }) {
  return (
    <div className="card p-5">
      <div className="text-xs text-ink-500 font-medium mb-1">{label}</div>
      <div className={`font-display text-2xl font-bold mb-1 ${accent || 'text-ink-50'}`}>{value}</div>
      {sub && <div className="text-xs text-ink-500">{sub}</div>}
    </div>
  )
}

function SentimentBadge({ s }) {
  const map = { positive: 'bg-lime/15 text-lime border-lime/30', negative: 'bg-red-500/15 text-red-400 border-red-500/30', neutral: 'bg-slate/15 text-slate-300 border-slate/30' }
  return <span className={`tag border ${map[s]}`}>{s}</span>
}

export default function Dashboard() {
  const totalRevenue = SALES.reduce((a, b) => a + b.revenue, 0)
  const totalUnits   = SALES.reduce((a, b) => a + b.units, 0)
  const topProduct   = [...SALES].sort((a, b) => b.revenue - a.revenue)[0]

  return (
    <div className="flex-1 overflow-auto p-6 space-y-6">
      {/* Header */}
      <div className="animate-fade-up">
        <h1 className="font-display text-2xl font-bold text-ink-50">Dashboard</h1>
        <p className="text-ink-400 text-sm mt-1">Sales performance & customer feedback overview</p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-up" style={{ animationDelay: '0.05s' }}>
        <StatCard label="Total Revenue" value={`$${(totalRevenue/1000).toFixed(1)}k`} sub="All products" accent="text-lime" />
        <StatCard label="Units Sold"    value={totalUnits} sub="This quarter" />
        <StatCard label="Top Product"   value={topProduct.product} sub={`$${topProduct.revenue.toLocaleString()}`} accent="text-slate-300" />
        <StatCard label="Satisfaction"  value="74%" sub="Positive feedback" accent="text-lime" />
      </div>

      {/* Charts row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 animate-fade-up" style={{ animationDelay: '0.1s' }}>
        {/* Revenue by product */}
        <div className="card p-5 lg:col-span-2">
          <h3 className="font-semibold text-ink-100 text-sm mb-4">Revenue by Product</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={SALES} barSize={24}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="product" tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(1)}k`} />
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [`$${v.toLocaleString()}`, 'Revenue']} />
              <Bar dataKey="revenue" fill="#C8F135" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Sentiment pie */}
        <div className="card p-5">
          <h3 className="font-semibold text-ink-100 text-sm mb-4">Feedback Sentiment</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={SENTIMENT} cx="50%" cy="50%" innerRadius={45} outerRadius={70} dataKey="value" paddingAngle={3}>
                {SENTIMENT.map((s, i) => <Cell key={i} fill={s.color} />)}
              </Pie>
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [`${v}%`, '']} />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-col gap-1.5 mt-3">
            {SENTIMENT.map(s => (
              <div key={s.name} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ background: s.color }} />
                  <span className="text-ink-400">{s.name}</span>
                </div>
                <span className="text-ink-200 font-mono">{s.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Charts row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-fade-up" style={{ animationDelay: '0.15s' }}>
        {/* Monthly trend */}
        <div className="card p-5">
          <h3 className="font-semibold text-ink-100 text-sm mb-4">Monthly Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={MONTHLY}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}k`} />
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [`$${v.toLocaleString()}`, 'Revenue']} />
              <Line type="monotone" dataKey="revenue" stroke="#C8F135" strokeWidth={2.5} dot={{ fill: '#C8F135', r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Units by product */}
        <div className="card p-5">
          <h3 className="font-semibold text-ink-100 text-sm mb-4">Units Sold by Product</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={SALES} barSize={20} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="product" tick={{ fill: '#78788a', fontSize: 11 }} axisLine={false} tickLine={false} width={60} />
              <Tooltip {...TOOLTIP_STYLE} formatter={v => [v, 'Units']} />
              <Bar dataKey="units" fill="#6B7A9F" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Feedback table */}
      <div className="card animate-fade-up" style={{ animationDelay: '0.2s' }}>
        <div className="px-5 py-4 border-b border-ink-800">
          <h3 className="font-semibold text-ink-100 text-sm">Recent Customer Feedback</h3>
        </div>
        <div className="divide-y divide-ink-800">
          {FEEDBACK.map(f => (
            <div key={f.id} className="flex items-start gap-4 px-5 py-3.5 hover:bg-ink-800/30 transition-colors">
              <div className="flex-1 min-w-0">
                <p className="text-sm text-ink-200 leading-relaxed">{f.text}</p>
                <p className="text-xs text-ink-600 mt-1 font-mono">{f.date}</p>
              </div>
              <div className="flex flex-col items-end gap-1.5 shrink-0">
                <SentimentBadge s={f.sentiment} />
                <span className="text-[10px] font-mono text-ink-500">score: {f.score.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
