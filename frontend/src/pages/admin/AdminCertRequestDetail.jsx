import { gql, useMutation, useQuery } from '@apollo/client'
import { useNavigate, useParams } from 'react-router-dom'
import { useMemo, useState } from 'react'
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

const DECIDE_REQUEST = gql`
  mutation AdminDecideCertRequestEmitEvent($requestId: String!, $decision: String!) {
    adminDecideCertRequestEmitEvent(requestId: $requestId, decision: $decision) {
      ok
      message
      eventId
    }
  }
`

function normalizeStatus(s) {
  const v = (s || '').toUpperCase().trim()
  return v || 'SUBMITTED'
}

function AdminCertRequestDetail() {
  const { id } = useParams()
  const navigate = useNavigate()

  const { loading, error, data, refetch } = useQuery(ADMIN_CERT_REQUESTS, {
    fetchPolicy: 'network-only',
  })

  const request = useMemo(() => {
    return data?.adminCertRequests?.find((r) => r.requestId === id) || null
  }, [data, id])

  const [decideRequest, { loading: deciding, error: decideError }] = useMutation(DECIDE_REQUEST)

  const status = normalizeStatus(request?.status)
  const canDecide = status === 'SUBMITTED'

  const [decision, setDecision] = useState('CONFIRMED')
  const [flash, setFlash] = useState('')

  const handleDecision = async () => {
    setFlash('')
    const res = await decideRequest({ variables: { requestId: id, decision } })
    const payload = res?.data?.adminDecideCertRequestEmitEvent
    if (payload?.ok) {
      setFlash(payload.message || 'Saved.')
      await refetch()
    } else {
      setFlash(payload?.message || 'Failed.')
    }
  }

  if (loading) return <div className="loading">Loading request…</div>
  if (error) return <div className="error">{error.message}</div>
  if (!request) return <div className="error">Request not found.</div>

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Request #{request.requestId}</h1>
        <button className="btn" onClick={() => navigate('/admin/cert-requests')}>Back</button>
      </div>

      <div className="card">
        <div className="detail-row">
          <span className="label">User</span>
          <span>{request.userId}</span>
        </div>
        <div className="detail-row">
          <span className="label">Vehicle</span>
          <span>{request.vehicleType} · {request.vehicleId}</span>
        </div>
        <div className="detail-row">
          <span className="label">License plate</span>
          <span>{request.licensePlate || '—'}</span>
        </div>
        <div className="detail-row">
          <span className="label">VIN</span>
          <span>{request.vehicleVin || '—'}</span>
        </div>
        <div className="detail-row">
          <span className="label">Year</span>
          <span>{request.requestYear || request.registrationYear || '—'}</span>
        </div>
        <div className="detail-row">
          <span className="label">Evidence</span>
          <span>{request.evidenceUrl || '—'}</span>
        </div>
        <div className="detail-row">
          <span className="label">Status</span>
          <span className={`badge status-${status.toLowerCase()}`}>{status}</span>
        </div>
        <div className="detail-row">
          <span className="label">Created</span>
          <span>{request.createdAt ? new Date(request.createdAt).toLocaleString() : '—'}</span>
        </div>
        <div className="detail-row">
          <span className="label">Decided</span>
          <span>{request.decidedAt ? new Date(request.decidedAt).toLocaleString() : '—'}</span>
        </div>
      </div>

      <div className="card actions">
        {!canDecide && (
          <div className="muted">
            This request is already decided. Decisions can only be made while status is SUBMITTED.
          </div>
        )}

        <div className="form">
          <label className="label">Set status</label>
          <select
            className="input"
            value={decision}
            onChange={(e) => setDecision(e.target.value)}
            disabled={!canDecide || deciding}
          >
            <option value="CONFIRMED">CONFIRMED</option>
            <option value="NEEDS_MORE_INFO">NEEDS_MORE_INFO</option>
            <option value="ERROR">ERROR</option>
            <option value="REJECTED">REJECTED</option>
          </select>

          <button
            className="btn primary"
            onClick={handleDecision}
            disabled={!canDecide || deciding}
          >
            {deciding ? 'Saving…' : 'Save status'}
          </button>
        </div>

        {flash && <div className="muted mt-1">{flash}</div>}
        {decideError && <div className="error mt-1">{decideError.message}</div>}
      </div>
    </div>
  )
}

export default AdminCertRequestDetail
