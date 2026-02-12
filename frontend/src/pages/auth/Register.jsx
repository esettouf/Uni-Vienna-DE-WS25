import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { gql, useMutation } from '@apollo/client'
import './Auth.css'

const REGISTER_MUTATION = gql`
  mutation RegisterUser(
    $email: String!
    $password: String!
    $passwordRepeat: String!
    $firstName: String!
    $lastName: String!
    $role: String
  ) {
    registerUser(
      email: $email
      password: $password
      passwordRepeat: $passwordRepeat
      firstName: $firstName
      lastName: $lastName
      role: $role
    ) {
      ok
      message
      userId
    }
  }
`

function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    password: '',
    passwordRepeat: '',
    firstName: '',
    lastName: '',
    role: 'customer',
  })
  const [registerMutate, { loading, error, data }] = useMutation(REGISTER_MUTATION)

  const onChange = (e) => {
    const { name, value } = e.target
    setForm((f) => ({ ...f, [name]: value }))
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    const { data } = await registerMutate({ variables: form })
    if (data?.registerUser?.ok) {
      navigate('/login')
    }
  }

  const message = data?.registerUser?.message

  return (
    <div className="auth-card card">
      <h1>Register</h1>
      <form onSubmit={onSubmit} className="auth-form">
        <label>First name</label>
        <input name="firstName" value={form.firstName} onChange={onChange} required />

        <label>Last name</label>
        <input name="lastName" value={form.lastName} onChange={onChange} required />

        <label>Email</label>
        <input name="email" type="email" value={form.email} onChange={onChange} required />

        <label>Account Type</label>
        <div className="radio-group">
          <label className="radio">
            <input
              type="radio"
              name="role"
              value="customer"
              checked={form.role === 'customer'}
              onChange={onChange}
            />
            <span>Individual (sell only)</span>
          </label>
          <label className="radio">
            <input
              type="radio"
              name="role"
              value="business"
              checked={form.role === 'business'}
              onChange={onChange}
            />
            <span>Business (buy & sell)</span>
          </label>
        </div>

        <label>Password</label>
        <input name="password" type="password" value={form.password} onChange={onChange} required />

        <label>Repeat Password</label>
        <input name="passwordRepeat" type="password" value={form.passwordRepeat} onChange={onChange} required />

        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>

        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error.message}</p>}
      </form>
      <p className="muted">Already have an account? <Link to="/login">Login</Link></p>
    </div>
  )
}

export default Register