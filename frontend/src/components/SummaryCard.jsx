function SummaryCard({ title, value, color }) {
  return (
    <div style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, flex: 1, textAlign: 'center' }}>
      <div style={{ color: '#666', fontSize: 14 }}>{title}</div>
      <div style={{ fontSize: 24, fontWeight: 'bold', color: color }}>{value}</div>
    </div>
  )
}

export default SummaryCard