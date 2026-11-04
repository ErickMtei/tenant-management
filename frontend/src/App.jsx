import { useState } from 'react'
import { getToken, logout } from './api'
import LoginForm from './components/LoginForm'
import Dashboard from './components/Dashboard'

function App() {
  const [loggedIn, setLoggedIn] = useState(Boolean(getToken()))

  function handleLogout() {
    logout()
    setLoggedIn(false)
  }

  if (!loggedIn) {
    return <LoginForm onLoggedIn={() => setLoggedIn(true)} />
  }

  return <Dashboard onLogout={handleLogout} />
}

export default App