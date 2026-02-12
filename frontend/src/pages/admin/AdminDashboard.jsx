import { gql, useQuery } from '@apollo/client'
import { Link } from 'react-router-dom'
import './Admin.css'

const USERS = gql`
  query UsersForDashboard {
    users {
      userId
      verificationStatus
    }
  }
`

const ADMIN_CERT_REQUESTS = gql`
  query AdminCertRequestsForDashboard {
    adminCertRequests {
      requestId
      status
    }
  }
`

function AdminDashboard() {
  const { loading: usersLoading, error: usersError, data: usersData } = useQuery(USERS)
  const { loading: reqLoading, error: reqError, data: reqData } = useQuery(ADMIN_CERT_REQUESTS)

  const users = usersData?.users || []
  const certRequests = reqData?.adminCertRequests || []

  const totalUsers = users.length
  const emailPending = users.filter((u) => u.verificationStatus === 'EMAIL_PENDING').length
  const kycSubmitted = users.filter((u) => u.verificationStatus === 'KYC_SUBMITTED').length
  const verified = users.filter((u) => u.verificationStatus === 'VERIFIED').length
  const pendingCerts = certRequests.filter((r) => r.status === 'SUBMITTED').length

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p className="muted">Overview and quick access</p>
      </div>

      {(usersLoading || reqLoading) && <div className="loading">Loading…</div>}
      {usersError && <div className="error">{usersError.message}</div>}
      {reqError && <div className="error">{reqError.message}</div>}

      <div className="card kpi-grid">
        <div className="kpi"><div className="kpi-label">Total users</div><div className="kpi-value">{totalUsers}</div></div>
        <div className="kpi"><div className="kpi-label">Email pending</div><div className="kpi-value">{emailPending}</div></div>
        <div className="kpi"><div className="kpi-label">KYC submitted</div><div className="kpi-value">{kycSubmitted}</div></div>
        <div className="kpi"><div className="kpi-label">Verified</div><div className="kpi-value">{verified}</div></div>
        <div className="kpi"><div className="kpi-label">Pending cert requests</div><div className="kpi-value">{pendingCerts}</div></div>
      </div>

      <div className="card actions">
        <Link className="btn" to="/admin/users">Manage users</Link>
        <Link className="btn" to="/admin/cert-requests">Certification requests</Link>
        <Link className="btn" to="/admin/trades">Trades</Link>
      </div>
    </div>
  )
}

export default AdminDashboard