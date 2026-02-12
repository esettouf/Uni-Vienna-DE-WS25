import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { gql, useMutation, useQuery } from '@apollo/client'
import './Cert.css'

const REQUEST_DETAIL = gql`
  query CertRequest($id: String!) {
    certRequest(requestId: $id) {
      requestId
      vehicleType
      vehicleId
      registrationYear
      licensePlate
      vehicleVin
      requestYear
      evidenceUrl
      status
      createdAt
      decidedAt
      updatedAt
      canSubmit
    }
  }
`

const UPDATE_REQUEST = gql`
  mutation UpdateCertificationRequest(
    $requestId: String!
    $vehicleType: String!
    $vehicleId: String
    $registrationYear: String!
    $requestYear: String
    $licensePlate: String!
    $vehicleVin: String!
    $evidenceUrl: String
  ) {
    updateCertificationRequest(
      requestId: $requestId
      vehicleType: $vehicleType
      vehicleId: $vehicleId
      registrationYear: $registrationYear
      requestYear: $requestYear
      licensePlate: $licensePlate
      vehicleVin: $vehicleVin
      evidenceUrl: $evidenceUrl
    ) {
      ok
      message
      requestId
    }
  }
`

function CertRequestDetail() {
  const { id } = useParams()
  const { loading, error, data, refetch } = useQuery(REQUEST_DETAIL, { variables: { id } })
  const [form, setForm] = useState({
    vehicleType: '',
    vehicleId: '',
    registrationYear: '',
    requestYear: '',
    licensePlate: '',
    vehicleVin: '',
    evidenceUrl: '',
  })
  const [updateMutate, { loading: saving, error: updateError, data: updateData }] = useMutation(UPDATE_REQUEST)

  const r = data?.certRequest

  useEffect(() => {
    if (r) {
      setForm({
        vehicleType: r.vehicleType || '',
        vehicleId: r.vehicleId || '',
        registrationYear: String(r.registrationYear || r.requestYear || ''),
        requestYear: String(r.requestYear || r.registrationYear || ''),
        licensePlate: r.licensePlate || '',
        vehicleVin: r.vehicleVin || '',
        evidenceUrl: r.evidenceUrl || '',
      })
    }
  }, [r])

  if (loading) return <div className="loading">Loading…</div>
  if (error) return <div className="error">{error.message}</div>
  if (!r) return <div className="error">Not found</div>

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    await updateMutate({ variables: { requestId: id, ...form } })
    await refetch()
  }

  return (
    <div className="cert-page">
      <div className="page-header">
        <h1>Request #{r.requestId}</h1>
        <p className="muted">Status: {r.status}</p>
      </div>
      <div className="card cert-card">
        <div className="cert-body">
          <div className="detail"><span className="label">Vehicle Type:</span><span>{r.vehicleType || 'n/a'}</span></div>
          <div className="detail"><span className="label">Vehicle ID:</span><span>{r.vehicleId || 'n/a'}</span></div>
          <div className="detail"><span className="label">Registration Year:</span><span>{r.registrationYear || r.requestYear || '—'}</span></div>
          <div className="detail"><span className="label">License Plate:</span><span>{r.licensePlate || '—'}</span></div>
          <div className="detail"><span className="label">VIN:</span><span>{r.vehicleVin || '—'}</span></div>
          <div className="detail"><span className="label">Evidence URL:</span><span>{r.evidenceUrl || '—'}</span></div>
          <div className="detail"><span className="label">Created:</span><span>{r.createdAt ? new Date(r.createdAt).toLocaleDateString() : '—'}</span></div>
          <div className="detail"><span className="label">Decided:</span><span>{r.decidedAt ? new Date(r.decidedAt).toLocaleDateString() : '—'}</span></div>
          <div className="detail"><span className="label">Updated:</span><span>{r.updatedAt ? new Date(r.updatedAt).toLocaleDateString() : '—'}</span></div>
        </div>
      </div>

      {r.canSubmit && (
        <div className="card">
          <h3>Edit and Resubmit</h3>
          <p className="muted">Update the details requested by the reviewer, then resubmit.</p>
          <form onSubmit={onSubmit} className="cert-form">
            <label>Vehicle Type</label>
            <select name="vehicleType" value={form.vehicleType} onChange={onChange} required>
              <option value="">Select type</option>
              <option value="BEV">Battery electric (BEV)</option>
              <option value="PHEV">Plug-in hybrid (PHEV)</option>
              <option value="OTHER">Other</option>
            </select>

            <label>Vehicle ID (optional)</label>
            <input name="vehicleId" value={form.vehicleId} onChange={onChange} placeholder="Leave blank to keep" />

            <label>Request Year</label>
            <input name="requestYear" value={form.requestYear} onChange={onChange} required />

            <label>Registration Year</label>
            <input name="registrationYear" value={form.registrationYear} onChange={onChange} required />

            <label>License Plate</label>
            <input name="licensePlate" value={form.licensePlate} onChange={onChange} required />

            <label>VIN</label>
            <input name="vehicleVin" value={form.vehicleVin} onChange={onChange} required />

            <label>Evidence URL (optional)</label>
            <input name="evidenceUrl" value={form.evidenceUrl} onChange={onChange} />

            <button className="btn btn-primary" type="submit" disabled={saving}>
              {saving ? 'Saving…' : 'Save & Resubmit'}
            </button>
            {updateData?.updateCertificationRequest?.message && (
              <p className={updateData.updateCertificationRequest.ok ? 'success' : 'error'}>
                {updateData.updateCertificationRequest.message}
              </p>
            )}
            {updateError && <p className="error">{updateError.message}</p>}
          </form>
        </div>
      )}
    </div>
  )
}

export default CertRequestDetail