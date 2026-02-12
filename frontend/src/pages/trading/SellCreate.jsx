import { gql, useMutation, useQuery } from '@apollo/client'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import './Trading.css'

const MY_SELLABLE_CERTS = gql`
  query MySellableCertificates {
    mySellableCertificates {
      certificateId
      vehicleId
      requestYear
      status
      amountCo2
      createdAt
    }
  }
`

const CREATE_SELL_ORDER = gql`
  mutation CreateSellOrder($certificateId: String!, $minPrice: String, $validUntil: String!) {
    createSellOrder(certificateId: $certificateId, minPrice: $minPrice, validUntil: $validUntil) {
      ok
      message
      sellOrderId
    }
  }
`

function SellCreate() {
  const navigate = useNavigate()
  const { loading, error, data } = useQuery(MY_SELLABLE_CERTS)
  const [createSellOrder, { loading: saving, error: saveError }] = useMutation(CREATE_SELL_ORDER, {
    refetchQueries: ['MySellOrders'],
  })
  const [selectedId, setSelectedId] = useState('')
  const [minPrice, setMinPrice] = useState('')
  const [validUntil, setValidUntil] = useState('')

  const certs = data?.mySellableCertificates || []

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!selectedId) return
    await createSellOrder({ variables: { certificateId: selectedId, minPrice: minPrice || null, validUntil } })
    navigate('/trading')
  }

  return (
    <div className="trading-page">
      <div className="page-header">
        <h1>Create Sell Order</h1>
        <p className="muted">Select a certificate and set your minimum price</p>
      </div>
      {loading && <div className="loading">Loading certificates…</div>}
      {error && <div className="error">{error.message}</div>}
      <div className="card">
        <form className="form" onSubmit={onSubmit}>
          <label className="label">Certificate</label>
          <select className="input" value={selectedId} onChange={(e) => setSelectedId(e.target.value)} required>
            <option value="">Select certificate</option>
            {certs.map((c) => (
              <option key={c.certificateId} value={c.certificateId}>
                {c.certificateId} — Vehicle {c.vehicleId} · Year {c.requestYear} · CO2 {c.amountCo2 ?? '—'}
              </option>
            ))}
          </select>

          <label className="label">Minimum Price (optional)</label>
          <input className="input" type="number" step="0.01" value={minPrice} onChange={(e) => setMinPrice(e.target.value)} placeholder="e.g. 100.00" />

          <label className="label">Valid Until</label>
          <input className="input" type="date" value={validUntil} onChange={(e) => setValidUntil(e.target.value)} required />

          <button className="btn primary" type="submit" disabled={saving}>
            {saving ? 'Creating…' : 'Create Sell Order'}
          </button>
          {saveError && <div className="error mt-1">{saveError.message}</div>}
        </form>
      </div>
    </div>
  )
}

export default SellCreate