import { useState } from 'react'
import { login } from '../api'

function LoginForm({ onLoggedIn }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    try {
      await login(username, password)
      onLoggedIn()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 300, margin: '4rem auto', fontFamily: 'sans-serif' }}>
      <h2>Login</h2>

      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ width: '100%', padding: 8, marginBottom: 8, boxSizing: 'border-box' }}
      />

      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ width: '100%', padding: 8, marginBottom: 8, boxSizing: 'border-box' }}
      />

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <button type="submit" style={{ padding: '8px 16px' }}>Log in</button>
    </form>
  )
}

export default LoginForm