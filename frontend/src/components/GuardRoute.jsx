import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'

function GuardRoute({ children, requiredRole, allowedRoles }) {
  const { isAuthed, role } = useAuth()
  const normalizedRole = (role || '').toLowerCase()
  if (!isAuthed) return <Navigate to="/login" replace />

  if (requiredRole && normalizedRole !== requiredRole.toLowerCase()) {
    return <Navigate to="/" replace />
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const allowedNormalized = allowedRoles.map((r) => (r || '').toLowerCase())
    if (!allowedNormalized.includes(normalizedRole)) {
      return <Navigate to="/" replace />
    }
  }

  return children
}

export default GuardRoute