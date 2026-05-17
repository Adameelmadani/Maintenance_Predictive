import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, RadialBarChart, RadialBar, Legend
} from 'recharts'
import { Heart, Clock, AlertTriangle, Wrench, TrendingUp, TrendingDown, Database, TestTube, Zap } from 'lucide-react'
import { api } from '../api'

const statusColor = (s) =>
  s === 'healthy' ? '#16a34a' : s === 'warning' ? '#ea580c' : '#dc2626'

/* ---------- Sub-components ---------- */
function GaugeRing({ value, label, color }) {
  const r = 85, c = 2 * Math.PI * r
  const offset = c - (value / 100) * c
  return (
    <div className="gauge-ring">
      <svg width="200" height="200" viewBox="0 0 200 200">
        <circle className="gauge-bg" cx="100" cy="100" r={r} />
        <circle
          className="gauge-fill"
          cx="100" cy="100" r={r}
          stroke={color}
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="gauge-center">
        <div className="value" style={{ color }}>{value.toFixed(1)}%</div>
        <div className="label">{label}</div>
      </div>
    </div>
  )
}

/* ---------- Dashboard Page ---------- */
export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => { api.getOverview().then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false)) }, [])

  if (loading) return <div className="loading-screen"><div className="spinner" /><div className="loading-text">Initializing Mission Control...</div></div>
  if (!data) return <div className="page-body"><p style={{ color: 'var(--red)' }}>Failed to load data. Ensure the API server is running on port 5000.</p></div>

  const pieCounts = [
    { name: 'Healthy', value: data.healthy_count, color: '#16a34a' },
    { name: 'Warning', value: data.warning_count, color: '#ea580c' },
    { name: 'Critical', value: data.critical_count, color: '#dc2626' },
  ]

  const distData = data.rul_distribution.bins.map((b, i) => ({
    range: b, count: data.rul_distribution.counts[i],
  }))

  return (
    <>
      <div className="page-header">
        <h1>MISSION CONTROL</h1>
        <p>Fleet Status Dashboard - Real-Time Engine Monitoring</p>
      </div>

      <div className="page-body">
        {/* KPI Row */}
        <div className="kpi-grid fade-in">
          <div className="kpi-card accent-cyan fade-in stagger-1">
            <div className="kpi-header">
              <span className="kpi-label">Fleet Health</span>
              <div className="kpi-icon cyan"><Heart size={20} /></div>
            </div>
            <div className="kpi-value">{data.fleet_health}%</div>
            <div className={`kpi-delta ${data.fleet_health > 50 ? 'positive' : 'negative'}`}>
              {data.fleet_health > 50 ? <TrendingUp size={14} style={{display:'inline', marginRight:4}} /> : <TrendingDown size={14} style={{display:'inline', marginRight:4}} />} {Math.abs(data.fleet_health - 50).toFixed(1)}% vs baseline
            </div>
          </div>

          <div className="kpi-card accent-orange fade-in stagger-2">
            <div className="kpi-header">
              <span className="kpi-label">Min RUL</span>
              <div className="kpi-icon orange"><Clock size={20} /></div>
            </div>
            <div className="kpi-value">{data.min_rul}</div>
            <div className={`kpi-delta ${data.min_rul > 30 ? 'positive' : 'negative'}`}>
              {data.min_rul <= 30 ? 'Critical' : data.min_rul <= 50 ? 'Warning' : 'OK'}
            </div>
          </div>

          <div className="kpi-card accent-red fade-in stagger-3">
            <div className="kpi-header">
              <span className="kpi-label">Engines at Risk</span>
              <div className="kpi-icon red"><AlertTriangle size={20} /></div>
            </div>
            <div className="kpi-value">{data.critical_count}</div>
            <div className={`kpi-delta ${data.critical_count === 0 ? 'positive' : 'negative'}`}>
              {data.critical_count === 0 ? 'All Safe' : `${data.critical_count} RUL ≤ 30`}
            </div>
          </div>

          <div className="kpi-card accent-purple fade-in stagger-4">
            <div className="kpi-header">
              <span className="kpi-label">Total Engines</span>
              <div className="kpi-icon purple"><Wrench size={20} /></div>
            </div>
            <div className="kpi-value">{data.total_engines}</div>
            <div className="kpi-delta neutral">
              {data.models_loaded} models active
            </div>
          </div>
        </div>

        {/* Gauge + Pie */}
        <div className="grid-2 section fade-in stagger-3">
          <div className="chart-container">
            <div className="chart-title">Fleet Health Index</div>
            <GaugeRing
              value={data.fleet_health}
              label="Fleet Health"
              color={data.fleet_health > 60 ? '#16a34a' : data.fleet_health > 30 ? '#ea580c' : '#dc2626'}
            />
            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <div className="badge badge-healthy" style={{ marginRight: 8 }}>Healthy &gt;50</div>
              <div className="badge badge-warning" style={{ marginRight: 8 }}>Warning 30-50</div>
              <div className="badge badge-critical">Critical ≤30</div>
            </div>
          </div>

          <div className="chart-container">
            <div className="chart-title">Fleet Status Distribution</div>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieCounts} cx="50%" cy="50%" innerRadius={60} outerRadius={95}
                  dataKey="value" paddingAngle={4} stroke="none">
                  {pieCounts.map((e, i) => <Cell key={i} fill={e.color} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#f0f4ff', border: '1px solid rgba(37,99,235,0.2)', borderRadius: 8, color: '#1f2937' }} />
                <Legend wrapperStyle={{ fontSize: '0.8rem', color: '#6b7280' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* RUL Distribution */}
        <div className="section fade-in stagger-4">
          <div className="chart-container">
            <div className="chart-title">RUL Distribution Across Fleet</div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={distData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <XAxis dataKey="range" tick={{ fill: '#6b7280', fontSize: 12 }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 12 }} />
                <Tooltip contentStyle={{ background: '#f0f4ff', border: '1px solid rgba(37,99,235,0.2)', borderRadius: 8, color: '#1f2937' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {distData.map((_, i) => (
                    <Cell key={i} fill={i < 2 ? '#dc2626' : i < 3 ? '#ea580c' : '#2563eb'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Engine Fleet Grid */}
        <div className="section fade-in stagger-5">
          <div className="section-title">Engine Fleet Status (Top 20)</div>
          <div className="engine-grid">
            {data.engines.slice(0, 20).map(eng => (
              <div
                key={eng.engine_id}
                className={`engine-card ${eng.status}`}
                onClick={() => navigate(`/prognostic?engine=${eng.engine_id}`)}
              >
                <div className="engine-id">
                  EN{String(eng.engine_id).padStart(3, '0')}
                </div>
                <div className="engine-rul">{eng.rul.toFixed(0)}</div>
                <div className="engine-label">RUL cycles</div>
                <div className={`badge badge-${eng.status}`} style={{ marginTop: 8, fontSize: '0.65rem' }}>
                  {eng.status.toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Platform Info */}
        <div className="section fade-in stagger-6">
          <div className="grid-3">
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 8, display:'flex', justifyContent:'center' }}><Database size={32} color="var(--cyan)" /></div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', color: 'var(--cyan)' }}>{data.train_samples.toLocaleString()}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Training Samples</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 8, display:'flex', justifyContent:'center' }}><TestTube size={32} color="var(--cyan)" /></div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', color: 'var(--cyan)' }}>{data.test_samples.toLocaleString()}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Test Samples</div>
            </div>
            <div className="card" style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 8, display:'flex', justifyContent:'center' }}><Zap size={32} color="var(--cyan)" /></div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', color: 'var(--cyan)' }}>{data.n_features}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Features</div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
