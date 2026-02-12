import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthProvider'

function ProtectedRoute({ children }) {
  const { isAuthed } = useAuth()
  if (!isAuthed) {
    return <Navigate to="/login" replace />
  }
  return children
}

export default ProtectedRoute
