import { gql, useQuery } from '@apollo/client'
import { Link } from 'react-router-dom'
import './Cert.css'

const CERTS_QUERY = gql`
  query MyCertificates {
    myCertificates {
      certificateId
      status
      vehicleId
      requestYear
      amountCo2
      createdAt
    }
    mySellableCertificates {
      certificateId
      status
      vehicleId
      requestYear
      amountCo2
      createdAt
    }
  }
`

function CertRow({ cert }) {
  return (
    <div className="card cert-card">
      <div className="cert-header">
        <div>
          <h3>Certificate #{cert.certificateId}</h3>
          <p className="muted">Vehicle: {cert.vehicleId || 'n/a'} · Year: {cert.requestYear}</p>
        </div>
        <span className={`status status-${(cert.status || '').toLowerCase()}`}>{cert.status}</span>
      </div>
      <div className="cert-body">
        <div className="detail"><span className="label">CO₂ Amount:</span><span>{cert.amountCo2 ?? '—'}</span></div>
        <div className="detail"><span className="label">Created:</span><span>{cert.createdAt ? new Date(cert.createdAt).toLocaleDateString() : '—'}</span></div>
      </div>
    </div>
  )
}

function Certificates() {
  const { loading, error, data } = useQuery(CERTS_QUERY)

  if (loading) return <div className="loading">Loading certificates…</div>
  if (error) return <div className="error">{error.message}</div>

  const certs = data?.myCertificates || []
  const sellable = data?.mySellableCertificates || []

  return (
    <div className="cert-page">
      <div className="page-header">
        <h1>My Certificates</h1>
        <p className="muted">Certificates issued to your account</p>
        <div className="page-actions">
          <Link className="btn btn-primary" to="/certification/submit">New Request</Link>
          <Link className="btn btn-secondary" to="/certification/requests">My requests</Link>
          <Link className="btn" to="/trading">Go to trading</Link>
        </div>
      </div>

      {certs.length === 0 ? (
        <div className="card"><p className="muted">No certificates yet.</p></div>
      ) : (
        certs.map((c) => <CertRow key={c.certificateId} cert={c} />)
      )}

      <div className="page-header" style={{ marginTop: '2rem' }}>
        <h2>Sellable Certificates</h2>
        <p className="muted">Certificates eligible for selling</p>
      </div>
      {sellable.length === 0 ? (
        <div className="card"><p className="muted">No sellable certificates.</p></div>
      ) : (
        sellable.map((c) => <CertRow key={`sell-${c.certificateId}`} cert={c} />)
      )}
    </div>
  )
}

export default Certificates