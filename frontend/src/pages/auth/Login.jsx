import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { gql, useMutation } from '@apollo/client'
import { useAuth } from '../../components/AuthProvider'
import './Auth.css'

const LOGIN_MUTATION = gql`
  mutation AuthLogin($email: String!, $password: String!) {
    authLogin(email: $email, password: $password) {
      ok
      message
      accessToken
      role
      userId
    }
  }
`

function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [form, setForm] = useState({ email: '', password: '' })
  const [loginMutate, { loading, error }] = useMutation(LOGIN_MUTATION)

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    const { data } = await loginMutate({ variables: form })
    const res = data?.authLogin
    if (res?.ok && res.accessToken) {
      login(res.accessToken, res.role)
      navigate('/')
    }
  }

  return (
    <div className="auth-card card">
      <h1>Login</h1>
      <form onSubmit={onSubmit} className="auth-form">
        <label>Email</label>
        <input name="email" type="email" value={form.email} onChange={onChange} required />

        <label>Password</label>
        <input name="password" type="password" value={form.password} onChange={onChange} required />

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Signing in...' : 'Login'}
        </button>

        {error && <p className="error">{error.message}</p>}
      </form>
      <p className="muted">No account? <Link to="/register">Register</Link></p>
    </div>
  )
}

export default Login