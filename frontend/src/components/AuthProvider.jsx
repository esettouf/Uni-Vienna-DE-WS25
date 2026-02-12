import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // Initialize from localStorage immediately to avoid a flash-redirect on refresh
  const [token, setToken] = useState(() => localStorage.getItem('auth_token'))
  const [role, setRole] = useState(() => localStorage.getItem('auth_role'))

  const login = (jwt, userRole) => {
    setToken(jwt)
    setRole(userRole || null)
    localStorage.setItem('auth_token', jwt)
    if (userRole) localStorage.setItem('auth_role', userRole)
  }

  const logout = () => {
    setToken(null)
    setRole(null)
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_role')
  }

  // Normalize role so UI can make capability decisions
  const normalizedRole = (role || '').toLowerCase()
  const isAdmin = normalizedRole === 'admin'
  const isBusiness = normalizedRole === 'business' || normalizedRole === 'company'
  const isCustomer = normalizedRole === 'customer' || normalizedRole === 'user'

  const value = {
    token,
    role,
    roleNormalized: normalizedRole,
    isAuthed: !!token,
    isAdmin,
    isBusiness,
    isCustomer,
    login,
    logout,
  }
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
