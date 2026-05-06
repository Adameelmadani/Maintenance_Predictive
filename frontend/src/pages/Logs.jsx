import { useState, useEffect } from 'react'
import { api } from '../api'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, XAxis, YAxis
} from 'recharts'

export default function Logs() {
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getOverview().then(d => { setOverview(d); setLoading(false) }).catch(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading-screen"><div className="spinner"/><div className="loading-text">Loading logs...</div></div>

  const tt = { background:'#182240', border:'1px solid rgba(0,212,255,0.2)', borderRadius:8, color:'#e8f4fd' }

  // Build simulated maintenance events from fleet data
  const engines = overview?.engines || []
  const criticalEngines = engines.filter(e => e.status === 'critical')
  const warningEngines = engines.filter(e => e.status === 'warning')

  const events = [
    ...criticalEngines.map(e => ({
      severity: 'CRITICAL',
      engine: `EN${String(e.engine_id).padStart(3,'0')}`,
      rul: e.rul,
      message: `IMMEDIATE MAINTENANCE — RUL = ${e.rul.toFixed(1)} cycles`,
      action: 'Shutdown recommended. Replace component urgently.',
      time: new Date().toLocaleString(),
    })),
    ...warningEngines.map(e => ({
      severity: 'WARNING',
      engine: `EN${String(e.engine_id).padStart(3,'0')}`,
      rul: e.rul,
      message: `Schedule maintenance — RUL = ${e.rul.toFixed(1)} cycles`,
      action: 'Plan maintenance within 20 cycles.',
      time: new Date().toLocaleString(),
    })),
    ...engines.filter(e => e.status === 'healthy').slice(0, 5).map(e => ({
      severity: 'INFO',
      engine: `EN${String(e.engine_id).padStart(3,'0')}`,
      rul: e.rul,
      message: `Normal operation — RUL = ${e.rul.toFixed(1)} cycles`,
      action: 'Continue normal operation.',
      time: new Date().toLocaleString(),
    })),
  ]

  const severityCounts = { CRITICAL: criticalEngines.length, WARNING: warningEngines.length, INFO: engines.length - criticalEngines.length - warningEngines.length }
  const pieData = [
    { name:'Critical', value:severityCounts.CRITICAL, color:'#ff3366' },
    { name:'Warning', value:severityCounts.WARNING, color:'#ff6b35' },
    { name:'Healthy', value:severityCounts.INFO, color:'#00ff88' },
  ]

  // Top problematic engines
  const topEngines = engines.filter(e => e.status !== 'healthy').sort((a,b) => a.rul - b.rul).slice(0, 10)
  const topData = topEngines.map(e => ({ name:`EN${String(e.engine_id).padStart(3,'0')}`, rul:e.rul }))

  const [filter, setFilter] = useState('ALL')
  const filtered = filter === 'ALL' ? events : events.filter(e => e.severity === filter)

  return (
    <>
      <div className="page-header"><h1>📋 MAINTENANCE LOG</h1><p>Event History — Alert Tracking — Analytics</p></div>
      <div className="page-body">
        {/* KPIs */}
        <div className="kpi-grid fade-in">
          <div className="kpi-card accent-red">
            <div className="kpi-header"><span className="kpi-label">Critical Alerts</span><span className="kpi-icon red">🚨</span></div>
            <div className="kpi-value">{severityCounts.CRITICAL}</div>
          </div>
          <div className="kpi-card accent-orange">
            <div className="kpi-header"><span className="kpi-label">Warnings</span><span className="kpi-icon orange">⚠️</span></div>
            <div className="kpi-value">{severityCounts.WARNING}</div>
          </div>
          <div className="kpi-card accent-green">
            <div className="kpi-header"><span className="kpi-label">Healthy</span><span className="kpi-icon green">✅</span></div>
            <div className="kpi-value">{severityCounts.INFO}</div>
          </div>
          <div className="kpi-card accent-cyan">
            <div className="kpi-header"><span className="kpi-label">Total Engines</span><span className="kpi-icon cyan">📊</span></div>
            <div className="kpi-value">{engines.length}</div>
          </div>
        </div>

        {/* Filter */}
        <div style={{ marginBottom:20 }} className="fade-in stagger-1">
          <select className="form-select" value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">🚨 Critical Only</option>
            <option value="WARNING">⚠️ Warning Only</option>
            <option value="INFO">✅ Info Only</option>
          </select>
        </div>

        {/* Events */}
        <div className="section fade-in stagger-2">
          <div className="section-title">📊 Event Log ({filtered.length} events)</div>
          {filtered.length === 0 ? (
            <div className="card" style={{ textAlign:'center', padding:40 }}>
              <div style={{ fontSize:'2rem', marginBottom:12 }}>✅</div>
              <div style={{ color:'var(--green)' }}>No events matching filter.</div>
            </div>
          ) : (
            filtered.map((evt, i) => (
              <div key={i} className={`alert-item ${evt.severity === 'CRITICAL' ? 'critical-alert' : evt.severity === 'WARNING' ? 'warning-alert' : 'info-alert'}`}>
                <div style={{ fontSize:'1.4rem' }}>{evt.severity === 'CRITICAL' ? '🚨' : evt.severity === 'WARNING' ? '⚠️' : '✅'}</div>
                <div className="alert-content">
                  <div className="alert-title" style={{ color: evt.severity === 'CRITICAL' ? 'var(--red)' : evt.severity === 'WARNING' ? 'var(--orange)' : 'var(--green)' }}>
                    {evt.severity} — {evt.engine}
                  </div>
                  <div className="alert-message">{evt.message}</div>
                  <div className="alert-meta">⚙️ {evt.action} · {evt.time}</div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Charts */}
        <div className="grid-2 section fade-in stagger-3">
          <div className="chart-container">
            <div className="chart-title">Alerts by Severity</div>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={85} dataKey="value" paddingAngle={4} stroke="none">
                  {pieData.map((e,i)=><Cell key={i} fill={e.color}/>)}
                </Pie>
                <Tooltip contentStyle={tt}/>
                <Legend wrapperStyle={{ fontSize:'0.78rem' }}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="chart-container">
            <div className="chart-title">Most Problematic Engines</div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={topData} layout="vertical">
                <XAxis type="number" tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                <YAxis type="category" dataKey="name" tick={{ fill:'#7e8fa6', fontSize:11 }} width={70}/>
                <Tooltip contentStyle={tt}/>
                <Bar dataKey="rul" radius={[0,4,4,0]} barSize={14}>
                  {topData.map((_,i)=><Cell key={i} fill={i<3?'#ff3366':'#ff6b35'}/>)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </>
  )
}
