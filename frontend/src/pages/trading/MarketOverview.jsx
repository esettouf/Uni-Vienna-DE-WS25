import { gql, useQuery } from '@apollo/client'
import './Trading.css'

const MARKET_SELL_ORDERS = gql`
  query MarketSellOrders {
    marketSellOrders {
      sellOrderId
      sellerId
      certificateId
      minPrice
      status
      createdAt
      expiresAt
    }
  }
`

const MARKET_BIDS = gql`
  query MarketBids {
    marketOpenBids {
      bidId
      companyId
      maxPrice
      status
      createdAt
      filledAt
    }
  }
`


function MarketOverview() {
  const {
    loading: sellLoading,
    error: sellError,
    data: sellData,
    refetch: refetchSell,
  } = useQuery(MARKET_SELL_ORDERS, { fetchPolicy: 'network-only' })

  const {
    loading: bidLoading,
    error: bidError,
    data: bidData,
    refetch: refetchBids,
  } = useQuery(MARKET_BIDS, { fetchPolicy: 'network-only' })

  const sellOrders = sellData?.marketSellOrders || []
  const bids = bidData?.marketOpenBids || []

  const isLoading = sellLoading || bidLoading
  const error = sellError || bidError

  return (
    <div className="trading-page">
      <div className="page-header">
        <h1>Market Overview</h1>
        <p className="muted">Open sell orders and open buy bids currently available</p>

        <div className="actions">
          <button className="btn" onClick={() => { refetchSell(); refetchBids(); }}>
            Refresh
          </button>
        </div>
      </div>

      {isLoading && <div className="loading">Loading…</div>}
      {error && <div className="error">{error.message}</div>}

      <div className="card">
        <h2 className="section-title">Sell Orders</h2>

        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Certificate</th>
                <th>Min price</th>
                <th>Status</th>
                <th>Created</th>
                <th>Expires</th>
              </tr>
            </thead>
            <tbody>
              {sellOrders.map((o) => (
                <tr key={o.sellOrderId}>
                  <td>{o.sellOrderId}</td>
                  <td>{o.certificateId}</td>
                  <td>{Number(o.minPrice || 0).toFixed(2)}</td>
                  <td>
                    <span className={`badge status-${(o.status || '').toLowerCase()}`}>
                      {o.status}
                    </span>
                  </td>
                  <td>{o.createdAt ? new Date(o.createdAt).toLocaleString() : '—'}</td>
                  <td>{o.expiresAt ? new Date(o.expiresAt).toLocaleString() : '—'}</td>
                </tr>
              ))}

              {!sellLoading && sellOrders.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted center">No sell orders.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card">
        <h2 className="section-title">Buy Bids</h2>

        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Company</th>
                <th>Max price</th>
                <th>Status</th>
                <th>Created</th>
                <th>Filled</th>
              </tr>
            </thead>
            <tbody>
              {bids.map((b) => (
                <tr key={b.bidId}>
                  <td>{b.bidId}</td>
                  <td>{b.companyId}</td>
                  <td>{Number(b.maxPrice || 0).toFixed(2)}</td>
                  <td>
                    <span className={`badge status-${(b.status || '').toLowerCase()}`}>
                      {b.status}
                    </span>
                  </td>
                  <td>{b.createdAt ? new Date(b.createdAt).toLocaleString() : '—'}</td>
                  <td>{b.filledAt ? new Date(b.filledAt).toLocaleString() : '—'}</td>
                </tr>
              ))}

              {!bidLoading && bids.length === 0 && (
                <tr>
                  <td colSpan={6} className="muted center">No bids.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default MarketOverview
