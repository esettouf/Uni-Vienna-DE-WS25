import { Link, useLocation } from 'react-router-dom'
import { useAuth } from './AuthProvider'
import './Layout.css'

function Layout({ children }) {
  const location = useLocation()
  const { isAuthed, isBusiness, role, logout } = useAuth()

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/' ? 'nav-active' : ''
    return location.pathname.startsWith(path) ? 'nav-active' : ''
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="container nav">
          <div className="brand">THG Exchange</div>
          <nav>
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              Home
            </Link>
            {isAuthed && (
              <>
                <Link to="/certification/requests" className={`nav-link ${isActive('/certification/requests')}`}>
                  Requests
                </Link>
                <Link to="/certificates" className={`nav-link ${isActive('/certificates')}`}>
                  Certificates
                </Link>
                <Link to="/trading" className={`nav-link ${isActive('/trading')}`}>
                  Sell Orders
                </Link>
                <Link to="/market" className={`nav-link ${isActive('/market')}`}>
                  Market Overview
                </Link>
                {isBusiness && (
                  <Link to="/trading/bids" className={`nav-link ${isActive('/trading/bids')}`}>
                    Bids
                  </Link>
                )}
              </>
            )}
            {isAuthed && role === 'admin' && (
              <>
                <Link to="/admin" className={`nav-link ${isActive('/admin')}`}>
                  Admin
                </Link>
              </>
            )}
            {!isAuthed && (
              <>
                <Link to="/login" className={`nav-link ${isActive('/login')}`}>
                  Login
                </Link>
                <Link to="/register" className={`nav-link ${isActive('/register')}`}>
                  Register
                </Link>
              </>
            )}
            {isAuthed && (
              <button className="btn btn-secondary" onClick={logout}>
                Logout
              </button>
            )}
          </nav>
        </div>
      </header>

      <main className="container main-content">
        {children}
      </main>

      <footer className="footer">
        <div className="container">
          &copy; 2026 THG Exchange
        </div>
      </footer>
    </div>
  )
}

export default Layout
