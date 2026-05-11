import { useState, useEffect } from 'react'

const KEY = 'agent_saved_queries'

export function useSavedQueries(userId) {
  const storageKey = `${KEY}_${userId}`
  const [queries, setQueries] = useState(() => {
    try { return JSON.parse(localStorage.getItem(storageKey) || '[]') }
    catch { return [] }
  })

  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(queries))
  }, [queries, storageKey])

  function save(query, label) {
    const entry = {
      id: Date.now(),
      label: label || query.slice(0, 60) + (query.length > 60 ? '…' : ''),
      query,
      createdAt: new Date().toISOString(),
      runCount: 0,
    }
    setQueries(prev => [entry, ...prev].slice(0, 50))
    return entry
  }

  function remove(id) {
    setQueries(prev => prev.filter(q => q.id !== id))
  }

  function incrementRun(id) {
    setQueries(prev => prev.map(q => q.id === id ? { ...q, runCount: q.runCount + 1, lastRun: new Date().toISOString() } : q))
  }

  function update(id, label) {
    setQueries(prev => prev.map(q => q.id === id ? { ...q, label } : q))
  }

  return { queries, save, remove, incrementRun, update }
}
