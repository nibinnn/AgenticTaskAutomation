const BASE = import.meta.env.VITE_API_URL || '/api'

async function request(method, path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`)
  return data
}

export const api = {
  health:          ()       => request('GET',  '/health'),
  solve:           (body)   => request('POST', '/pipeline/solve', body),
  agents:          ()       => request('GET',  '/pipeline/agents'),
  analyzeData:     (body)   => request('POST', '/data/analyze', body),
  filterData:      (body)   => request('POST', '/data/filter', body),
  aggregateData:   (body)   => request('POST', '/data/aggregate', body),
  classifyText:    (body)   => request('POST', '/ai/classify', body),
  summarizeText:   (body)   => request('POST', '/ai/summarize', body),
}
