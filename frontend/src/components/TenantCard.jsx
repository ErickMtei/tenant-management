function TenantCard({ tenant }) {
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, marginBottom: 8 }}>
      <strong>{tenant.full_name}</strong>
      <div>Phone: {tenant.phone_number}</div>
      <div>Unit: {tenant.unit}</div>
    </div>
  )
}

export default TenantCard