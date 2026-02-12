import { gql, useMutation, useQuery } from '@apollo/client'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import './Trading.css'

const MY_SELL_ORDERS = gql`
  query MySellOrders {
    mySellOrders {
      sellOrderId
      certificateId
      minPrice
      status
      tradeId
      matchedAt
      expiresAt
      createdAt
    }
    myTrades {
      tradeId
      sellOrderId
      price
      fee
      net
      status
      createdAt
    }
  }
`

function SellOrders() {
  const { loading, error, data } = useQuery(MY_SELL_ORDERS)
  const [cancelOrder, { loading: cancelling }] = useMutation(gql`
    mutation CancelSellOrder($sellOrderId: String!) {
      cancelSellOrder(sellOrderId: $sellOrderId) { ok message sellOrderId }
    }
  `, { refetchQueries: ['MySellOrders'] })

  const [updateOrder, { loading: updating }] = useMutation(gql`
    mutation UpdateSellOrder($sellOrderId: String!, $minPrice: String, $validUntil: String!) {
      updateSellOrder(sellOrderId: $sellOrderId, minPrice: $minPrice, validUntil: $validUntil) {
        ok
        message
        sellOrderId
      }
    }
  `, { refetchQueries: ['MySellOrders'] })

  const [editState, setEditState] = useState({})

  if (loading) return <div className="loading">Loading sell orders…</div>
  if (error) return <div className="error">{error.message}</div>

  const orders = data?.mySellOrders || []
  const tradeMap = (data?.myTrades || []).reduce((acc, t) => {
    acc[t.sellOrderId] = t
    return acc
  }, {})

  const startEdit = (order) => {
    setEditState((s) => ({
      ...s,
      [order.sellOrderId]: {
        minPrice: order.minPrice ?? '',
        validUntil: order.expiresAt ? order.expiresAt.slice(0, 10) : '',
      },
    }))
  }

  const onEditChange = (orderId, field, value) => {
    setEditState((s) => ({
      ...s,
      [orderId]: { ...(s[orderId] || {}), [field]: value },
    }))
  }

  const submitEdit = async (orderId) => {
    const state = editState[orderId]
    if (!state) return
    await updateOrder({ variables: { sellOrderId: orderId, minPrice: state.minPrice || null, validUntil: state.validUntil } })
  }

  return (
    <div className="trading-page">
      <div className="page-header">
        <h1>My Sell Orders</h1>
        <div className="page-actions">
          <p className="muted">Track your active and past sell orders</p>
          <Link className="btn btn-primary" to="/trading/sell-create">Create sell order</Link>
          <Link className="btn btn-secondary" to="/certificates">Certificates</Link>
        </div>
      </div>
      {orders.length === 0 ? (
        <div className="card"><p className="muted">No sell orders yet.</p></div>
      ) : (
        <div className="trade-list">
          {orders.map((o) => (
            <div key={o.sellOrderId} className="card trade-card">
              <div className="trade-header">
                <div>
                  <h3>Sell Order #{o.sellOrderId}</h3>
                  <p className="muted">Certificate: {o.certificateId}</p>
                </div>
                <span className={`status status-${(o.status || '').toLowerCase()}`}>{o.status}</span>
              </div>
              <div className="trade-body">
                <div className="detail"><span className="label">Min Price:</span><span>{o.minPrice ?? '—'}</span></div>
                <div className="detail"><span className="label">Valid Until:</span><span>{o.expiresAt ? o.expiresAt.slice(0, 10) : '—'}</span></div>
                <div className="detail"><span className="label">Created:</span><span>{o.createdAt ? new Date(o.createdAt).toLocaleDateString() : '—'}</span></div>
                <div className="detail"><span className="label">Matched:</span><span>{o.matchedAt ? new Date(o.matchedAt).toLocaleDateString() : '—'}</span></div>
                <div className="detail"><span className="label">Trade ID:</span><span>{o.tradeId || '—'}</span></div>
                {o.tradeId && tradeMap[o.sellOrderId] && (
                  <>
                    <div className="detail"><span className="label">Trade Price:</span><span>{tradeMap[o.sellOrderId].price}</span></div>
                    <div className="detail"><span className="label">Fee:</span><span>{tradeMap[o.sellOrderId].fee}</span></div>
                    <div className="detail"><span className="label">Net:</span><span>{tradeMap[o.sellOrderId].net}</span></div>
                  </>
                )}
              </div>
              {o.status === 'PLACED' && (
                <div className="trade-actions">
                  <button className="btn btn-secondary" onClick={() => startEdit(o)} disabled={updating}>Edit</button>
                  <button className="btn btn-danger" onClick={() => cancelOrder({ variables: { sellOrderId: o.sellOrderId } })} disabled={cancelling}>Cancel</button>
                </div>
              )}
              {o.status === 'PLACED' && editState[o.sellOrderId] && (
                <div className="trade-edit">
                  <label className="label">Min Price</label>
                  <input
                    className="input"
                    type="number"
                    step="0.01"
                    value={editState[o.sellOrderId].minPrice}
                    onChange={(e) => onEditChange(o.sellOrderId, 'minPrice', e.target.value)}
                  />
                  <label className="label">Valid Until</label>
                  <input
                    className="input"
                    type="date"
                    value={editState[o.sellOrderId].validUntil}
                    onChange={(e) => onEditChange(o.sellOrderId, 'validUntil', e.target.value)}
                    required
                  />
                  <button className="btn primary" onClick={() => submitEdit(o.sellOrderId)} disabled={updating}>
                    {updating ? 'Saving…' : 'Save'}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SellOrders