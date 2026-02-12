import { gql, useMutation, useQuery } from '@apollo/client'
import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../../components/AuthProvider'
import './Trading.css'

const ALL_BIDS = gql`
  query AllBids {
    allBids {
      bidId
      companyId
      maxPrice
      status
      createdAt
      filledAt
    }
  }
`

const CREATE_BID = gql`
  mutation CreateBid($companyId: String, $maxPrice: String!) {
    createBid(companyId: $companyId, maxPrice: $maxPrice) {
      ok
      message
      bidId
    }
  }
`

function Bids() {
  const { isBusiness } = useAuth()
  if (!isBusiness) {
    return <Navigate to="/trading" replace />
  }

  const { loading, error, data } = useQuery(ALL_BIDS)
  const [createBid, { loading: saving, error: saveError }] = useMutation(CREATE_BID, {
    refetchQueries: ['AllBids'],
  })
  const [companyId, setCompanyId] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  const bids = data?.allBids || []

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!maxPrice) return
    await createBid({ variables: { companyId: companyId || null, maxPrice } })
    setCompanyId('')
    setMaxPrice('')
  }

  return (
    <div className="trading-page">
      <div className="page-header">
        <h1>Bids</h1>
        <p className="muted">Place a bid on available sell orders and track their status</p>
      </div>
      <div className="card">
        <form className="form" onSubmit={onSubmit}>
          <label className="label">Company ID (optional)</label>
          <input className="input" value={companyId} onChange={(e) => setCompanyId(e.target.value)} placeholder="company_demo" />

          <label className="label">Max Price</label>
          <input className="input" type="number" step="0.01" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} placeholder="e.g. 120.00" required />

          <button className="btn primary" type="submit" disabled={saving}>
            {saving ? 'Submitting…' : 'Place Bid'}
          </button>
          {saveError && <div className="error mt-1">{saveError.message}</div>}
        </form>
      </div>

      {loading && <div className="loading">Loading bids…</div>}
      {error && <div className="error">{error.message}</div>}

      {bids.length === 0 ? (
        <div className="card"><p className="muted">No bids yet.</p></div>
      ) : (
        <div className="trade-list">
          {bids.map((b) => (
            <div key={b.bidId} className="card trade-card">
              <div className="trade-header">
                <div>
                  <h3>Bid #{b.bidId}</h3>
                  <p className="muted">Company: {b.companyId || '—'}</p>
                </div>
                <span className={`status status-${(b.status || '').toLowerCase()}`}>{b.status}</span>
              </div>
              <div className="trade-body">
                <div className="detail"><span className="label">Max Price:</span><span>{b.maxPrice}</span></div>
                <div className="detail"><span className="label">Created:</span><span>{b.createdAt ? new Date(b.createdAt).toLocaleDateString() : '—'}</span></div>
                <div className="detail"><span className="label">Filled:</span><span>{b.filledAt ? new Date(b.filledAt).toLocaleDateString() : '—'}</span></div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Bids