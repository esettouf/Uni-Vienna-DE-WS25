import { gql, useQuery } from '@apollo/client'
import { Link, useNavigate } from 'react-router-dom'
import './Admin.css'

const ADMIN_CERT_REQUESTS = gql`
  query AdminCertRequests {
    adminCertRequests {
      requestId
      userId
      vehicleType
      vehicleId
      licensePlate
      vehicleVin
      registrationYear
      requestYear
      evidenceUrl
      status
      createdAt
      decidedAt
    }
  }
`

function normalizeStatus(s) {
  const v = (s || '').toUpperCase().trim()
  return v || 'SUBMITTED'
}

function AdminCertRequests() {
  const navigate = useNavigate()
  const { loading, error, data } = useQuery(ADMIN_CERT_REQUESTS, {
    fetchPolicy: 'network-only',
  })
  const requests = data?.adminCertRequests || []

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Admin · Certification Requests</h1>
        <p className="muted">Review and manage incoming certification requests</p>
      </div>

      {loading && <div className="loading">Loading requests…</div>}
      {error && <div className="error">{error.message}</div>}

      <div className="card">
        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Vehicle</th>
                <th>Plate</th>
                <th>VIN</th>
                <th>Req year</th>
                <th>Status</th>
                <th>Created</th>
                <th>Decision</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((r) => {
                const status = normalizeStatus(r.status)
                const isDecided = status !== 'SUBMITTED'

                return (
                  <tr key={r.requestId}>
                    <td>
                      <Link to={`/admin/cert-requests/${r.requestId}`} className="link">
                        {r.requestId}
                      </Link>
                    </td>
                    <td>{r.userId}</td>
                    <td>{r.vehicleType} · {r.vehicleId}</td>
                    <td>{r.licensePlate || '—'}</td>
                    <td>{r.vehicleVin || '—'}</td>
                    <td>{r.requestYear || r.registrationYear || '—'}</td>
                    <td>
                      <span className={`badge status-${status.toLowerCase()}`}>
                        {status}
                      </span>
                    </td>
                    <td>{r.createdAt ? new Date(r.createdAt).toLocaleDateString() : '—'}</td>
                    <td>
                      <button
                        className="btn"
                        onClick={() => navigate(`/admin/cert-requests/${r.requestId}`)}
                      >
                        {isDecided ? 'View' : 'Review'}
                      </button>
                    </td>
                  </tr>
                )
              })}

              {!loading && requests.length === 0 && (
                <tr>
                  <td colSpan={9} className="muted center">No certification requests.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default AdminCertRequests
