import { gql, useMutation, useQuery } from '@apollo/client'
import { useMemo, useState } from 'react'
import './Admin.css'

const USERS = gql`
  query Users {
    users {
      userId
      email
      fullName
      role
      verificationStatus
      walletBalance
      createdAt
    }
  }
`

const UPDATE_STATUS = gql`
  mutation UpdateVerificationStatus($userId: String!, $status: String!) {
    updateVerificationStatus(userId: $userId, status: $status) {
      ok
      message
    }
  }
`

const DELETE_USER = gql`
  mutation DeleteUser($userId: String!) {
    deleteUser(userId: $userId) {
      ok
      message
    }
  }
`

const VERIFICATION_OPTIONS = [
  'EMAIL_PENDING',
  'IDENTITY_PENDING',
  'KYC_SUBMITTED',
  'VERIFIED',
  'REJECTED',
  'MANUAL_REVIEW',
]

function AdminUsers() {
  const { loading, error, data, refetch } = useQuery(USERS)
  const [updateStatus, { loading: updating }] = useMutation(UPDATE_STATUS, {
    update(cache, { variables }) {
      if (!variables?.userId || !variables?.status) return
      const existing = cache.readQuery({ query: USERS })
      if (!existing?.users) return
      cache.writeQuery({
        query: USERS,
        data: {
          users: existing.users.map((u) =>
            u.userId === variables.userId ? { ...u, verificationStatus: variables.status } : u
          ),
        },
      })
    },
  })
  const [deleteUser, { loading: deleting }] = useMutation(DELETE_USER)
  const [sortBy, setSortBy] = useState('fullName')
  const [filterRole, setFilterRole] = useState('all')

  const handleStatusChange = async (userId, status) => {
    await updateStatus({ variables: { userId, status } })
  }

  const handleDelete = async (userId) => {
    if (!window.confirm('Delete this user?')) return
    await deleteUser({ variables: { userId } })
    refetch()
  }

  const users = data?.users || []

  const roles = useMemo(
    () => [...new Set(users.map((u) => u.role).filter(Boolean))],
    [users]
  )

  const filteredSorted = useMemo(() => {
    let list = [...users]
    if (filterRole !== 'all') {
      list = list.filter((u) => u.role === filterRole)
    }
    list.sort((a, b) => {
      const aVal = a?.[sortBy] ?? ''
      const bVal = b?.[sortBy] ?? ''
      return String(aVal).localeCompare(String(bVal))
    })
    return list
  }, [users, filterRole, sortBy])

  return (
    <div className="admin-page">
      <div className="page-header">
        <h1>Admin · Users</h1>
        <p className="muted">View accounts and manage verification status</p>
      </div>

      {loading && <div className="loading">Loading users…</div>}
      {error && <div className="error">{error.message}</div>}

      <div className="controls card">
        <div className="control-group">
          <label htmlFor="sort-by">Sort by</label>
          <select id="sort-by" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="fullName">Name</option>
            <option value="email">Email</option>
            <option value="role">Role</option>
            <option value="verificationStatus">Status</option>
            <option value="createdAt">Joined</option>
          </select>
        </div>
        <div className="control-group">
          <label htmlFor="filter-role">Filter by role</label>
          <select
            id="filter-role"
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
          >
            <option value="all">All Roles</option>
            {roles.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="users-stats card">
        <p>
          Showing <strong>{filteredSorted.length}</strong> of{' '}
          <strong>{users.length}</strong> users
        </p>
      </div>

      <div className="users-list">
        {!loading && filteredSorted.length === 0 && (
          <div className="card">
            <p className="muted">No users found.</p>
          </div>
        )}
        {filteredSorted.map((u) => (
          <div key={u.userId} className="user-card card">
            <div className="user-header">
              <div>
                <h3>{u.fullName || 'N/A'}</h3>
                <p className="user-email">{u.email}</p>
              </div>
              <span className={`badge badge-${(u.role || '').toLowerCase()}`}>{u.role}</span>
            </div>
            <div className="user-details">
              <div className="detail-item">
                <span className="detail-label">Status</span>
                <select
                  className="input"
                  value={u.verificationStatus || ''}
                  onChange={(e) => handleStatusChange(u.userId, e.target.value)}
                  disabled={updating}
                >
                  {VERIFICATION_OPTIONS.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              </div>
              <div className="detail-item">
                <span className="detail-label">Wallet</span>
                <span className="detail-value">€ {u.walletBalance?.toFixed(2) ?? '0.00'}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Joined</span>
                <span className="detail-value">
                  {u.createdAt ? new Date(u.createdAt).toLocaleDateString() : '—'}
                </span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Actions</span>
                <button
                  className="btn danger"
                  onClick={() => handleDelete(u.userId)}
                  disabled={deleting}
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AdminUsers