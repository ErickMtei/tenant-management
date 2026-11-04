const API_URL = import.meta.env.VITE_API_URL

export function getToken() {
  return localStorage.getItem('access_token')
}

export function logout() {
  localStorage.removeItem('access_token')
}

export async function login(username, password) {
  const response = await fetch(`${API_URL}/token/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    throw new Error('Wrong username or password')
  }

  const data = await response.json()
  localStorage.setItem('access_token', data.access)
}

export async function apiGet(path) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })

  if (response.status === 401) {
    logout()
    throw new Error('Session expired. Please log in again.')
  }
  if (!response.ok) {
    throw new Error('Failed to load data')
  }

  return response.json()
}