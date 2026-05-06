import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  LineChart, Line, AreaChart, Area, ReferenceLine
} from 'recharts'
import { api } from '../api'

function GaugeRing({ value, label, color }) {
  const r = 85, c = 2 * Math.PI * r, offset = c - (value / 100) * c
  return (
    <div className="gauge-ring">
      <svg width="200" height="200" viewBox="0 0 200 200">
        <circle className="gauge-bg" cx="100" cy="100" r={r}/>
        <circle className="gauge-fill" cx="100" cy="100" r={r} stroke={color} strokeDasharray={c} strokeDashoffset={offset}/>
      </svg>
      <div className="gauge-center">
        <div className="value" style={{ color }}>{value.toFixed(1)}%</div>
        <div className="label">{label}</div>
      </div>
    </div>
  )
}

export default function Prognostic() {
  const [searchParams] = useSearchParams()
  const [engineId, setEngineId] = useState(+searchParams.get('engine') || 1)
  const [engines, setEngines] = useState([])
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => { api.getEngines().then(d => setEngines(d.engine_ids)).catch(() => {}) }, [])
  useEffect(() => {
    setLoading(true)
    api.getEngine(engineId).then(d => { setData(d); setLoading(false) }).catch(() => setLoading(false))
  }, [engineId])

  if (loading) return <div className="loading-screen"><div className="spinner"/><div className="loading-text">Analyzing engine...</div></div>
  if (!data) return <div className="page-body"><p style={{ color:'var(--red)' }}>Engine not found.</p></div>

  const statusColor = data.status === 'healthy' ? '#00ff88' : data.status === 'warning' ? '#ff6b35' : '#ff3366'
  const statusLabel = data.status.toUpperCase()
  const tt = { background:'#182240', border:'1px solid rgba(0,212,255,0.2)', borderRadius:8, color:'#e8f4fd' }

  const predData = Object.entries(data.predictions || {}).sort((a,b) => a[1] - b[1]).map(([n,v]) => ({ name:n, rul:v }))
  const rulHistory = (data.cycles || []).map((c,i) => ({ cycle:c, rul: data.rul_history?.[i] || 0 }))

  const prescClass = data.rul > 50 ? 'normal' : data.rul > 30 ? 'warning' : data.rul > 15 ? 'urgent' : 'critical'
  const p = data.prescription || {}

  return (
    <>
      <div className="page-header"><h1>🔮 PROGNOSTIC CENTER</h1><p>Real-Time RUL Estimation & Forecasting</p></div>
      <div className="page-body">
        <div style={{ marginBottom:20 }} className="fade-in">
          <select className="form-select" value={engineId} onChange={e=>setEngineId(+e.target.value)}>
            {engines.map(id=><option key={id} value={id}>EN{String(id).padStart(3,'0')}</option>)}
          </select>
        </div>

        {/* KPI Row */}
        <div className="kpi-grid fade-in stagger-1">
          <div className="kpi-card accent-cyan">
            <div className="kpi-header"><span className="kpi-label">Engine</span><span className="kpi-icon cyan">🚀</span></div>
            <div className="kpi-value">EN{String(data.engine_id).padStart(3,'0')}</div>
            <div className="kpi-delta neutral">Cycle {data.current_cycle}</div>
          </div>
          <div className="kpi-card accent-orange">
            <div className="kpi-header"><span className="kpi-label">Predicted RUL</span><span className="kpi-icon orange">⏱️</span></div>
            <div className="kpi-value">{data.rul.toFixed(1)}</div>
            <div className="kpi-delta neutral">cycles remaining</div>
          </div>
          <div className="kpi-card" style={{ borderTop:`2px solid ${statusColor}` }}>
            <div className="kpi-header"><span className="kpi-label">Health Status</span></div>
            <div style={{ textAlign:'center', padding:'8px 0' }}>
              <span className={`badge badge-${data.status}`} style={{ fontSize:'0.85rem', padding:'8px 20px' }}>{statusLabel}</span>
            </div>
            <div style={{ textAlign:'center', fontFamily:'var(--font-heading)', fontSize:'1.5rem', color:statusColor, marginTop:8 }}>{data.health_index}%</div>
          </div>
        </div>

        {/* Gauge + Prescription */}
        <div className="grid-2 section fade-in stagger-2">
          <div className="chart-container" style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div className="chart-title" style={{ alignSelf:'flex-start' }}>Health Index Gauge</div>
            <GaugeRing value={data.health_index} label="Health" color={statusColor}/>
            <div style={{ marginTop:16, display:'flex', gap:8 }}>
              <div className="badge badge-healthy" style={{ fontSize:'0.65rem' }}>🟢 60-100%</div>
              <div className="badge badge-warning" style={{ fontSize:'0.65rem' }}>🟡 30-60%</div>
              <div className="badge badge-critical" style={{ fontSize:'0.65rem' }}>🔴 0-30%</div>
            </div>
          </div>
          <div className={`prescription ${prescClass}`}>
            <h3 style={{ color:statusColor }}>🔧 {p.status || 'N/A'}</h3>
            <ul>
              <li><strong>Action:</strong> {p.action}</li>
              <li><strong>Risk Level:</strong> {p.risk}</li>
              <li><strong>Next Check:</strong> {p.next_check}</li>
            </ul>
          </div>
        </div>

        {/* RUL History */}
        {rulHistory.length > 0 && (
          <div className="section fade-in stagger-3">
            <div className="chart-container">
              <div className="chart-title">RUL History</div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={rulHistory}>
                  <defs>
                    <linearGradient id="rulGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="cycle" tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                  <YAxis tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                  <Tooltip contentStyle={tt}/>
                  <ReferenceLine y={30} stroke="#ff3366" strokeDasharray="4 4" label={{ value:'Critical', fill:'#ff3366', fontSize:11 }}/>
                  <Area type="monotone" dataKey="rul" stroke="#00d4ff" fill="url(#rulGrad)" strokeWidth={2}/>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Multi-Model Comparison */}
        {predData.length > 0 && (
          <div className="section fade-in stagger-4">
            <div className="chart-container">
              <div className="chart-title">Multi-Model RUL Comparison</div>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={predData} layout="vertical">
                  <XAxis type="number" tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                  <YAxis type="category" dataKey="name" tick={{ fill:'#7e8fa6', fontSize:11 }} width={110}/>
                  <Tooltip contentStyle={tt}/>
                  <Bar dataKey="rul" radius={[0,6,6,0]} barSize={20}>
                    {predData.map((_,i)=><Cell key={i} fill={`hsl(${200-i*30},80%,55%)`}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
