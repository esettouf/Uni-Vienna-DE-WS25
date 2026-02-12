import { gql, useQuery } from '@apollo/client'
import './Admin.css'

const ADMIN_TRADES = gql`
  query AdminTrades {
    adminTrades {
      tradeId
      certificateId
      sellOrderId
      bidId
      companyId
      price
      fee
      net
      status
      blockchainHash
      createdAt
    }
  }
`

function AdminTrades() {
  const { loading, error, data, refetch } = useQuery(ADMIN_TRADES, {
    fetchPolicy: 'network-only',
  })

  const trades = data?.adminTrades || []

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Admin · Trades</h1>
        <p className="muted">All executed trades in the system</p>

        <button className="btn" onClick={() => refetch()}>
          Refresh
        </button>
      </div>

      {loading && <div className="loading">Loading trades…</div>}
      {error && <div className="error">{error.message}</div>}

      <div className="card">
        <div className="table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Trade</th>
                <th>Certificate</th>
                <th>Sell order</th>
                <th>Bid</th>
                <th>Company</th>
                <th>Price</th>
                <th>Fee</th>
                <th>Net</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((t) => (
                <tr key={t.tradeId}>
                  <td>{t.tradeId}</td>
                  <td>{t.certificateId}</td>
                  <td>{t.sellOrderId}</td>
                  <td>{t.bidId}</td>
                  <td>{t.companyId}</td>
                  <td>{Number(t.price || 0).toFixed(2)}</td>
                  <td>{Number(t.fee || 0).toFixed(2)}</td>
                  <td>{Number(t.net || 0).toFixed(2)}</td>
                  <td>
                    <span className={`badge status-${(t.status || '').toLowerCase()}`}>
                      {t.status}
                    </span>
                  </td>
                  <td>{t.createdAt ? new Date(t.createdAt).toLocaleString() : '—'}</td>
                </tr>
              ))}

              {!loading && trades.length === 0 && (
                <tr>
                  <td colSpan={10} className="muted center">No trades.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default AdminTrades
