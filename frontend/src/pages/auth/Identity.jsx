import { useState } from 'react'
import { gql, useMutation } from '@apollo/client'
import './Auth.css'

const SUBMIT_IDENTITY = gql`
  mutation SubmitIdentity($docType: String!, $docRef: String!) {
    submitIdentity(docType: $docType, docRef: $docRef) {
      ok
      message
    }
  }
`

function Identity() {
  const [form, setForm] = useState({ docType: '', docRef: '' })
  const [submitMutate, { loading, error, data }] = useMutation(SUBMIT_IDENTITY)

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    await submitMutate({ variables: form })
  }

  const message = data?.submitIdentity?.message

  return (
    <div className="auth-card card">
      <h1>Identity Verification</h1>
      <p className="muted">Provide your identity document for verification.</p>
      <form onSubmit={onSubmit} className="auth-form">
        <label>Document Type</label>
        <input name="docType" value={form.docType} onChange={onChange} required />

        <label>Document Reference</label>
        <input name="docRef" value={form.docRef} onChange={onChange} required />

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Identity'}
        </button>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error.message}</p>}
      </form>
    </div>
  )
}

export default Identity