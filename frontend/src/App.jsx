import { useState } from 'react'
import TenantCard from './components/TenantCard'

const tenants = [
  { id: 1, full_name: 'Juma Hassan', phone_number: '0711000001', unit: 'A1' },
  { id: 2, full_name: 'Asha Mohamed', phone_number: '0711000002', unit: 'A2' },
  { id: 3, full_name: 'Peter Mushi', phone_number: '0711000003', unit: 'A3' },
]

function App() {
  const [search, setSearch] = useState('')

  const filtered = tenants.filter((tenant) =>
    tenant.full_name.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div style={{ maxWidth: 600, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Tenant Management</h1>

      <input
        type="text"
        placeholder="Search by name..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        style={{ width: '100%', padding: 8, marginBottom: 12 }}
      />

      <p>{filtered.length} tenant(s) found</p>

      {filtered.map((tenant) => (
        <TenantCard key={tenant.id} tenant={tenant} />
      ))}
    </div>
  )
}

export default App