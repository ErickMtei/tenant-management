import { useEffect, useState } from 'react'
import { apiGet, formatMoney } from '../api'
import SummaryCard from './SummaryCard'

function currentMonth() {
  // Returns e.g. "2026-11"
  return new Date().toISOString().slice(0, 7)
}

function SummaryCards() {
  const [month, setMonth] = useState(currentMonth())
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadSummary() {
      try {
        setError('')
        const data = await apiGet(`/reports/summary/?month=${month}`)
        setSummary(data)
      } catch (err) {
        setError(err.message)
      }
    }
    loadSummary()
  }, [month])

  return (
    <div style={{ marginBottom: 16 }}>
      <label>
        Month:{' '}
        <input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
        />
      </label>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!summary && !error && <p>Loading summary...</p>}

      {summary && (
        <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
          <SummaryCard title="Expected rent" value={formatMoney(summary.rent.expected)} color="blue" />
          <SummaryCard title="Collected" value={formatMoney(summary.rent.collected)} color="green" />
          <SummaryCard title="Outstanding" value={formatMoney(summary.rent.outstanding)} color="red" />
          <SummaryCard title="Vacant units" value={summary.units.vacant} color="orange" />
        </div>
      )}
    </div>
  )
}

export default SummaryCards