import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <div className="hero">
        <h1>Welcome to THG Exchange</h1>
        <p className="subtitle">A transparent marketplace for trading green house gas certificates</p>
      </div>

      <ProfilePayoutSection />

      <div className="features">
        <div className="feature-card card">
          <h3>Browse Certificates</h3>
          <p>Explore available carbon credits and sustainability certificates from verified sources.</p>
          <Link to="/certificates" className="btn btn-primary">View Certificates</Link>
        </div>

        <div className="feature-card card">
          <h3>Manage Your Portfolio</h3>
          <p>Track your certificates, submit verification requests, and manage your holdings.</p>
          <Link to="/certificates" className="btn btn-primary">Manage Portfolio</Link>
        </div>

        <div className="feature-card card">
          <h3>Trade & Sell</h3>
          <p>Create sell orders and place bids on available certificates in the marketplace.</p>
          <Link to="/trading" className="btn btn-primary">Start Trading</Link>
        </div>
      </div>

      <section className="info-section card">
        <h2>How it Works</h2>
        <ol className="steps">
          <li><strong>Register</strong> and complete personal or dentity verification</li>
          <li><strong>Submit</strong> your sustainability certificates for certification</li>
          <li><strong>B2B: Sell</strong> or <strong>Buy</strong> certificates through our transparent marketplace</li>
          <li><strong>Track</strong> your transactions and portfolio performance</li>
          <li><strong>Withdraw</strong> your balance</li>
        </ol>
      </section>
    </div>
  )
}

import { gql, useMutation, useQuery } from '@apollo/client'
import { useMemo, useState } from 'react'

const PROFILE_PAYOUT = gql`
  query ProfilePayout {
    currentUser {
      email
      role
      verificationStatus
      walletBalance
      hasBankDetails
      ibanMasked
    }
  }
`

const SET_BANK_DETAILS = gql`
  mutation SetBankDetails($iban: String!, $holder: String!, $bic: String) {
    setBankDetails(iban: $iban, holder: $holder, bic: $bic) {
      ok
      message
    }
  }
`

const REQUEST_PAYOUT = gql`
  mutation RequestPayout {
    requestPayout {
      ok
      message
    }
  }
`

function ProfilePayoutSection() {
  const { data, loading, error, refetch } = useQuery(PROFILE_PAYOUT)
  const [setBankDetails] = useMutation(SET_BANK_DETAILS)
  const [requestPayout, { loading: requesting }] = useMutation(REQUEST_PAYOUT)

  const user = data?.currentUser
  const [showForm, setShowForm] = useState(false)
  const [iban, setIban] = useState('')
  const [holder, setHolder] = useState('')
  const [bic, setBic] = useState('')
  const [msg, setMsg] = useState('')

  const canWithdraw = useMemo(() => {
    if (!user) return false
    return (
      user.verificationStatus === 'VERIFIED' &&
      user.walletBalance > 0 &&
      user.hasBankDetails
    )
  }, [user])

  if (loading) return null
  if (error || !user) return null

  return (
    <section className="card profile-payout">
      <h2>Your Profile</h2>

      <div className="profile-grid">
        <div>
          <span className="label">Status</span>
          <div>{user.verificationStatus}</div>
        </div>
        <div>
          <span className="label">Wallet</span>
          <div>€ {Number(user.walletBalance ?? 0).toFixed(2)}</div>
        </div>
        <div>
          <span className="label">Bank account</span>
          <div>{user.hasBankDetails ? user.ibanMasked : 'Not set'}</div>
        </div>
      </div>

      <div className="profile-actions">
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          {user.hasBankDetails ? 'Update bank details' : 'Add bank details'}
        </button>

        <button
          className="btn btn-primary"
          disabled={!canWithdraw || requesting}
          onClick={async () => {
            const res = await requestPayout()
            setMsg(res?.data?.requestPayout?.message || '')
            refetch()
          }}
        >
          Withdraw balance
        </button>
      </div>

      {showForm && (
        <form
          className="bank-form"
          onSubmit={async (e) => {
            e.preventDefault()
            const res = await setBankDetails({
              variables: { iban, holder, bic: bic || null },
            })
            setMsg(res?.data?.setBankDetails?.message || '')
            setShowForm(false)
            refetch()
          }}
        >
          <input className="input" placeholder="Account holder" value={holder} onChange={(e) => setHolder(e.target.value)} />
          <input className="input" placeholder="IBAN" value={iban} onChange={(e) => setIban(e.target.value)} />
          <input className="input" placeholder="BIC (optional)" value={bic} onChange={(e) => setBic(e.target.value)} />

          <button className="btn btn-primary">Save bank details</button>
        </form>
      )}

      {msg && <div className="muted">{msg}</div>}
    </section>
  )
}


export default Home