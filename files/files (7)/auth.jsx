import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

const MOCK_USERS = [
  { id: 1, name: 'Arjun Sharma', email: 'arjun@acme.io', role: 'Admin', avatar: 'AS' },
  { id: 2, name: 'Priya Nair',   email: 'priya@acme.io', role: 'Analyst', avatar: 'PN' },
]

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [error, setError] = useState('')

  function login(email, password) {
    const found = MOCK_USERS.find(u => u.email === email)
    if (found && password === 'demo123') {
      setUser(found)
      setError('')
      return true
    }
    setError('Invalid email or password')
    return false
  }

  function logout() { setUser(null) }

  return (
    <AuthContext.Provider value={{ user, login, logout, error, setError }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
