import { useEffect, useState } from 'react'
import { apiGet } from '../api'
import SummaryCard from './SummaryCard'
import TenantCard from './TenantCard'

function Dashboard({ onLogout }) {
  const [tenants, setTenants] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    async function loadData() {
      try {
        const data = await apiGet('/tenants/')
        setTenants(data.results)
      } catch (err) {
        setError(err.message)
        if (err.message.startsWith('Session expired')) {
          onLogout()
        }
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const filtered = tenants.filter(
    (tenant) =>
      tenant.full_name.toLowerCase().includes(search.toLowerCase()) ||
      tenant.phone_number.includes(search)
  )

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Tenant Management</h1>
        <button onClick={onLogout}>Log out</button>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
        <SummaryCard title="Total tenants" value={tenants.length} color="blue" />
      </div>

      <input
        type="text"
        placeholder="Search by name or phone..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        style={{ width: '100%', padding: 8, marginBottom: 12, boxSizing: 'border-box' }}
      />

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {filtered.map((tenant) => (
        <TenantCard key={tenant.id} tenant={tenant} />
      ))}
    </div>
  )
}

export default Dashboard