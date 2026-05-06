import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, AreaChart, Area, RadialBarChart, RadialBar, Legend,
  LineChart, Line
} from 'recharts'
import { api } from '../api'

function MiniGauge({ value, max, color, label }) {
  const pct = Math.min((value / max) * 100, 100)
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ position: 'relative', width: 120, height: 120, margin: '0 auto' }}>
        <svg width="120" height="120" viewBox="0 0 120 120" style={{ transform: 'rotate(-90deg)' }}>
          <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="8" />
          <circle cx="60" cy="60" r="50" fill="none" stroke={color} strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={2 * Math.PI * 50}
            strokeDashoffset={2 * Math.PI * 50 * (1 - pct / 100)}
            style={{ transition: 'stroke-dashoffset 1s ease' }}
          />
        </svg>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', textAlign: 'center' }}>
          <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.2rem', fontWeight: 800, color }}>{value.toFixed(1)}</div>
        </div>
      </div>
      <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 6 }}>{label}</div>
    </div>
  )
}

export default function KPIs() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getKPIs().then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading-screen"><div className="spinner" /><div className="loading-text">Computing KPIs...</div></div>
  if (!data) return <div className="page-body"><p style={{ color: 'var(--red)' }}>Failed to load KPIs.</p></div>

  const statusPie = [
    { name: 'Healthy', value: data.status_distribution.healthy, color: '#00ff88' },
    { name: 'Warning', value: data.status_distribution.warning, color: '#ff6b35' },
    { name: 'Critical', value: data.status_distribution.critical, color: '#ff3366' },
  ]

  // Simulated trend data for visual richness
  const trendData = Array.from({ length: 12 }, (_, i) => ({
    month: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i],
    availability: 85 + Math.random() * 12,
    oee: 60 + Math.random() * 25,
    mtbf: 50 + Math.random() * 40,
  }))

  return (
    <>
      <div className="page-header">
        <h1>📊 KPI CENTER</h1>
        <p>Key Performance Indicators — Operational Intelligence & Analytics</p>
      </div>

      <div className="page-body">
        {/* Primary KPIs */}
        <div className="kpi-grid fade-in">
          <div className="kpi-card accent-green fade-in stagger-1">
            <div className="kpi-header">
              <span className="kpi-label">Fleet Availability</span>
              <span className="kpi-icon green">🟢</span>
            </div>
            <div className="kpi-value">{data.fleet_availability}%</div>
            <div className={`kpi-delta ${data.fleet_availability > 90 ? 'positive' : 'negative'}`}>
              {data.fleet_availability > 90 ? '▲ Excellent' : '▼ Below target'}
            </div>
          </div>

          <div className="kpi-card accent-cyan fade-in stagger-2">
            <div className="kpi-header">
              <span className="kpi-label">Mean RUL</span>
              <span className="kpi-icon cyan">⏱️</span>
            </div>
            <div className="kpi-value">{data.avg_rul}</div>
            <div className="kpi-delta neutral">σ = {data.std_rul} cycles</div>
          </div>

          <div className="kpi-card accent-purple fade-in stagger-3">
            <div className="kpi-header">
              <span className="kpi-label">MTBF Estimate</span>
              <span className="kpi-icon purple">🔄</span>
            </div>
            <div className="kpi-value">{data.mtbf_estimate}</div>
            <div className="kpi-delta neutral">cycles between failures</div>
          </div>

          <div className="kpi-card accent-yellow fade-in stagger-4">
            <div className="kpi-header">
              <span className="kpi-label">OEE Score</span>
              <span className="kpi-icon yellow">🏭</span>
            </div>
            <div className="kpi-value">{data.oee}%</div>
            <div className={`kpi-delta ${data.oee > 70 ? 'positive' : 'negative'}`}>
              {data.oee > 70 ? '▲ Above target' : '▼ Needs improvement'}
            </div>
          </div>
        </div>

        {/* Second KPI row */}
        <div className="kpi-grid fade-in stagger-2">
          <div className="kpi-card accent-red">
            <div className="kpi-header">
              <span className="kpi-label">Maintenance Due</span>
              <span className="kpi-icon red">🔧</span>
            </div>
            <div className="kpi-value">{data.maintenance_due}</div>
            <div className={`kpi-delta ${data.maintenance_due === 0 ? 'positive' : 'negative'}`}>
              {data.maintenance_due === 0 ? 'No urgent actions' : 'Immediate attention needed'}
            </div>
          </div>

          <div className="kpi-card accent-orange">
            <div className="kpi-header">
              <span className="kpi-label">Engines at Risk</span>
              <span className="kpi-icon orange">⚠️</span>
            </div>
            <div className="kpi-value">{data.engines_at_risk}</div>
            <div className="kpi-delta neutral">of {data.total_engines} total</div>
          </div>

          <div className="kpi-card accent-cyan">
            <div className="kpi-header">
              <span className="kpi-label">Prediction Accuracy</span>
              <span className="kpi-icon cyan">🎯</span>
            </div>
            <div className="kpi-value">{data.prediction_accuracy}%</div>
            <div className="kpi-delta positive">Best: {data.best_model.name}</div>
          </div>

          <div className="kpi-card accent-green">
            <div className="kpi-header">
              <span className="kpi-label">Data Coverage</span>
              <span className="kpi-icon green">📡</span>
            </div>
            <div className="kpi-value">{data.sensor_count}</div>
            <div className="kpi-delta neutral">{data.data_points.toLocaleString()} data points</div>
          </div>
        </div>

        {/* Gauges Row */}
        <div className="section fade-in stagger-3">
          <div className="section-title">🎯 Performance Gauges</div>
          <div className="grid-3">
            <div className="chart-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 30 }}>
              <MiniGauge value={data.fleet_availability} max={100} color="#00ff88" label="Availability %" />
            </div>
            <div className="chart-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 30 }}>
              <MiniGauge value={data.oee} max={100} color="#00d4ff" label="OEE Score" />
            </div>
            <div className="chart-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 30 }}>
              <MiniGauge value={data.prediction_accuracy} max={100} color="#7b2fbe" label="Model Accuracy %" />
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid-2 section fade-in stagger-4">
          <div className="chart-container">
            <div className="chart-title">Fleet Status Breakdown</div>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusPie} cx="50%" cy="50%" innerRadius={55} outerRadius={90}
                  dataKey="value" paddingAngle={4} stroke="none">
                  {statusPie.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#182240', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, color: '#e8f4fd' }} />
                <Legend wrapperStyle={{ fontSize: '0.8rem' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-container">
            <div className="chart-title">Performance Trend (12-Month Simulation)</div>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={trendData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <defs>
                  <linearGradient id="gradAvail" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00ff88" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradOEE" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#00d4ff" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" tick={{ fill: '#7e8fa6', fontSize: 11 }} />
                <YAxis tick={{ fill: '#7e8fa6', fontSize: 11 }} domain={[50, 100]} />
                <Tooltip contentStyle={{ background: '#182240', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, color: '#e8f4fd' }} />
                <Area type="monotone" dataKey="availability" stroke="#00ff88" fill="url(#gradAvail)" strokeWidth={2} name="Availability" />
                <Area type="monotone" dataKey="oee" stroke="#00d4ff" fill="url(#gradOEE)" strokeWidth={2} name="OEE" />
                <Legend wrapperStyle={{ fontSize: '0.78rem' }} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Summary Table */}
        <div className="section fade-in stagger-5">
          <div className="chart-container">
            <div className="chart-title">KPI Summary Table</div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>KPI</th>
                  <th>Value</th>
                  <th>Target</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Fleet Availability</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.fleet_availability}%</td>
                  <td>≥ 90%</td>
                  <td><span className={`badge badge-${data.fleet_availability >= 90 ? 'healthy' : 'warning'}`}>{data.fleet_availability >= 90 ? 'ON TARGET' : 'BELOW'}</span></td>
                </tr>
                <tr>
                  <td>Mean RUL</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.avg_rul} cycles</td>
                  <td>≥ 50</td>
                  <td><span className={`badge badge-${data.avg_rul >= 50 ? 'healthy' : 'warning'}`}>{data.avg_rul >= 50 ? 'ON TARGET' : 'BELOW'}</span></td>
                </tr>
                <tr>
                  <td>MTBF Estimate</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.mtbf_estimate} cycles</td>
                  <td>≥ 80</td>
                  <td><span className={`badge badge-${data.mtbf_estimate >= 80 ? 'healthy' : 'warning'}`}>{data.mtbf_estimate >= 80 ? 'ON TARGET' : 'BELOW'}</span></td>
                </tr>
                <tr>
                  <td>OEE Score</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.oee}%</td>
                  <td>≥ 70%</td>
                  <td><span className={`badge badge-${data.oee >= 70 ? 'healthy' : 'warning'}`}>{data.oee >= 70 ? 'ON TARGET' : 'BELOW'}</span></td>
                </tr>
                <tr>
                  <td>Prediction Accuracy</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.prediction_accuracy}%</td>
                  <td>≥ 85%</td>
                  <td><span className={`badge badge-${data.prediction_accuracy >= 85 ? 'healthy' : 'warning'}`}>{data.prediction_accuracy >= 85 ? 'ON TARGET' : 'BELOW'}</span></td>
                </tr>
                <tr>
                  <td>Critical Engines</td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>{data.maintenance_due}</td>
                  <td>0</td>
                  <td><span className={`badge badge-${data.maintenance_due === 0 ? 'healthy' : 'critical'}`}>{data.maintenance_due === 0 ? 'CLEAR' : 'ACTION NEEDED'}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  )
}
