import { useState } from 'react'
import { gql, useMutation } from '@apollo/client'
import './Cert.css'

const SUBMIT_CERT = gql`
  mutation SubmitCertificationRequest(
    $vehicleType: String!
    $vehicleId: String
    $registrationYear: String!
    $requestYear: String
    $licensePlate: String!
    $vehicleVin: String!
    $evidenceUrl: String
  ) {
    submitCertificationRequest(
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

function CertSubmit() {
  const [form, setForm] = useState({
    vehicleType: '',
    vehicleId: '',
    registrationYear: '',
    requestYear: '',
    licensePlate: '',
    vehicleVin: '',
    evidenceUrl: '',
  })
  const [submitMutate, { loading, error, data }] = useMutation(SUBMIT_CERT)

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    await submitMutate({ variables: form })
  }

  const res = data?.submitCertificationRequest

  return (
    <div className="cert-page">
      <div className="page-header">
        <h1>Submit Certification Request</h1>
        <p className="muted">Provide vehicle details to request a certificate.</p>
      </div>
      <div className="card">
        <form onSubmit={onSubmit} className="cert-form">
          <label>Vehicle Type</label>
          <select name="vehicleType" value={form.vehicleType} onChange={onChange} required>
            <option value="">Select type</option>
            <option value="BEV">Battery electric (BEV)</option>
            <option value="PHEV">Plug-in hybrid (PHEV)</option>
            <option value="OTHER">Other</option>
          </select>

          <label>Vehicle ID (optional)</label>
          <input name="vehicleId" value={form.vehicleId} onChange={onChange} placeholder="Leave blank to auto-generate" />

          <label>Request Year</label>
          <input name="requestYear" value={form.requestYear} onChange={onChange} placeholder="2025" required />

          <label>Registration Year</label>
          <input name="registrationYear" value={form.registrationYear} onChange={onChange} placeholder="2024" required />

          <label>License Plate</label>
          <input name="licensePlate" value={form.licensePlate} onChange={onChange} required />

          <label>VIN</label>
          <input name="vehicleVin" value={form.vehicleVin} onChange={onChange} placeholder="Vehicle identification number" required />

          <label>Evidence URL (optional)</label>
          <input name="evidenceUrl" value={form.evidenceUrl} onChange={onChange} placeholder="Link to evidence (PDF, cloud, etc.)" />

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Submitting…' : 'Submit Request'}
          </button>

          {res?.message && <p className={res.ok ? 'success' : 'error'}>{res.message}</p>}
          {error && <p className="error">{error.message}</p>}
        </form>
      </div>
    </div>
  )
}

export default CertSubmit