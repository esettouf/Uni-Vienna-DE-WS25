import { Link } from 'react-router-dom'
import { gql, useQuery } from '@apollo/client'
import './Cert.css'

const MY_REQUESTS = gql`
  query MyRequests {
    myCertRequests {
      requestId
      vehicleType
      vehicleId
      registrationYear
      requestYear
      licensePlate
      vehicleVin
      evidenceUrl
      status
      createdAt
      decidedAt
      updatedAt
      canSubmit
    }
  }
`

function CertRequests() {
  const { loading, error, data } = useQuery(MY_REQUESTS)

  if (loading) return <div className="loading">Loading requests…</div>
  if (error) return <div className="error">{error.message}</div>

  const requests = data?.myCertRequests || []

  return (
    <div className="cert-page">
      <div className="page-header">
        <h1>My Certification Requests</h1>
        <p className="muted">Track your submitted requests or start a new one.</p>
        <div className="page-actions">
          <Link className="btn btn-primary" to="/certification/submit">New request</Link>
          <Link className="btn btn-secondary" to="/certificates">Certificates</Link>
        </div>
      </div>
      {requests.length === 0 ? (
        <div className="card"><p className="muted">No requests yet.</p></div>
      ) : (
        <div className="cert-list">
          {requests.map((r) => (
            <div key={r.requestId} className="card cert-card">
              <div className="cert-header">
                <div>
                  <h3>Request #{r.requestId}</h3>
                  <p className="muted">
                    {r.vehicleType || 'Vehicle'} · Plate: {r.licensePlate || 'n/a'} · Year: {r.registrationYear || '—'}
                  </p>
                </div>
                <span className={`status status-${(r.status || '').toLowerCase()}`}>{r.status}</span>
              </div>
              <div className="cert-body">
                <div className="detail"><span className="label">Created:</span><span>{r.createdAt ? new Date(r.createdAt).toLocaleDateString() : '—'}</span></div>
                <div className="detail"><span className="label">Request Year:</span><span>{r.requestYear || r.registrationYear || '—'}</span></div>
                <div className="detail"><span className="label">Decided:</span><span>{r.decidedAt ? new Date(r.decidedAt).toLocaleDateString() : '—'}</span></div>
                <div className="detail"><span className="label">VIN:</span><span>{r.vehicleVin || '—'}</span></div>
                <div className="detail"><span className="label">Evidence:</span><span>{r.evidenceUrl ? 'Provided' : '—'}</span></div>
              </div>
              <Link to={`/certification/requests/${r.requestId}`} className="btn btn-secondary">
                View
              </Link>
              {r.canSubmit && <span className="hint">Needs more info — edit to resubmit.</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default CertRequests