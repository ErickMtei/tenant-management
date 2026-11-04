import { useState } from 'react'

function TenantCard({ tenant }) {
  const [paid, setPaid] = useState(false)

  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, marginBottom: 8 }}>
      <strong>{tenant.full_name}</strong>
      <div>Phone: {tenant.phone_number}</div>
      <button
        onClick={() => setPaid(!paid)}
        style={{
          marginTop: 8,
          padding: '4px 12px',
          color: 'white',
          border: 'none',
          borderRadius: 4,
          backgroundColor: paid ? 'green' : 'red',
        }}
      >
        {paid ? 'Paid' : 'Unpaid'}
      </button>
    </div>
  )
}

export default TenantCard