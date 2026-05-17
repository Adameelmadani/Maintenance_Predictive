import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, ZAxis
} from 'recharts'
import { Award } from 'lucide-react'
import { api } from '../api'

export default function IALab() {
  const [bench, setBench] = useState(null)
  const [tab, setTab] = useState('regression')
  const [selModel, setSelModel] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => { api.getBenchmarks().then(d => { setBench(d); setLoading(false) }).catch(() => setLoading(false)) }, [])

  if (loading) return <div className="loading-screen"><div className="spinner"/><div className="loading-text">Loading benchmarks...</div></div>
  if (!bench) return <div className="page-body"><p style={{ color:'var(--red)' }}>Benchmark results not found.</p></div>

  const rul = bench.RUL_Models?.benchmarks || {}
  const cls = bench.Classification_Models?.benchmarks || {}
  const rulDetailed = bench.RUL_Models?.detailed_results || {}
  const clsMatrices = bench.Classification_Models?.confusion_matrices || {}
  const tt = { background:'#f0f4ff', border:'1px solid rgba(37,99,235,0.2)', borderRadius:8, color:'#1f2937' }

  const rulEntries = Object.entries(rul).sort((a,b) => a[1].MAE - b[1].MAE)
  const barData = rulEntries.map(([n,m]) => ({ name:n, MAE:m.MAE, RMSE:m.RMSE }))

  const radarData = [
    { metric:'MAE Score', ...Object.fromEntries(rulEntries.map(([n,m])=>[n, 100/(m.MAE+1)])) },
    { metric:'RMSE Score', ...Object.fromEntries(rulEntries.map(([n,m])=>[n, 100/(m.RMSE+1)])) },
    { metric:'R² Score', ...Object.fromEntries(rulEntries.map(([n,m])=>[n, Math.max(0,m.R2*100+100)])) },
    { metric:'Speed', ...Object.fromEntries(rulEntries.map(([n,m])=>[n, 100/(m.TrainTime_s+0.1)])) },
  ]
  const colors = ['#2563eb','#16a34a','#ea580c','#dc2626','#7c3aed']
  const medals = ['Gold', 'Silver', 'Bronze']

  const currentModel = selModel || (rulEntries[0]?.[0] || '')
  const modelDetail = rulDetailed[currentModel]
  const scatterData = modelDetail ? modelDetail.y_actual.slice(0,300).map((a,i) => ({
    actual: a, predicted: modelDetail.y_pred[i], error: Math.abs(a - modelDetail.y_pred[i])
  })) : []

  return (
    <>
      <div className="page-header"><h1>IA LAB - BENCHMARKING</h1><p>Model Performance Comparison & Analysis</p></div>
      <div className="page-body">
        <div className="tabs fade-in">
          <button className={`tab ${tab==='regression'?'active':''}`} onClick={()=>setTab('regression')}>Regression (RUL)</button>
          <button className={`tab ${tab==='classification'?'active':''}`} onClick={()=>setTab('classification')}>Classification</button>
        </div>

        {tab === 'regression' && <>
          {/* Best models */}
          <div className="kpi-grid fade-in stagger-1">
            {rulEntries.slice(0,3).map(([n,m],i) => (
              <div key={n} className={`kpi-card accent-${['cyan','green','orange'][i]}`}>
                <div className="kpi-header"><span className="kpi-label">#{i+1} - {n}</span><div className={`kpi-icon ${['cyan','green','orange'][i]}`}><Award size={20} /></div></div>
                <div className="kpi-value" style={{ fontSize:'1.4rem' }}>{m.MAE.toFixed(2)}</div>
                <div className="kpi-delta neutral">MAE · R²={m.R2.toFixed(4)}</div>
              </div>
            ))}
          </div>

          {/* Performance Table */}
          <div className="section fade-in stagger-2">
            <div className="chart-container">
              <div className="chart-title">Performance Metrics</div>
              <table className="data-table">
                <thead><tr><th>Rank</th><th>Model</th><th>MAE</th><th>RMSE</th><th>R²</th><th>Train Time</th></tr></thead>
                <tbody>
                  {rulEntries.map(([n,m],i)=>(
                    <tr key={n}>
                      <td>{i+1}</td>
                      <td style={{ fontWeight:600, color:'var(--cyan)' }}>{n}</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{m.MAE.toFixed(2)}</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{m.RMSE.toFixed(2)}</td>
                      <td style={{ fontFamily:'var(--font-mono)', color: m.R2>0?'var(--green)':'var(--red)' }}>{m.R2.toFixed(4)}</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{m.TrainTime_s.toFixed(3)}s</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Charts */}
          <div className="grid-2 section fade-in stagger-3">
            <div className="chart-container">
              <div className="chart-title">MAE / RMSE Comparison</div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={barData} layout="vertical">
                  <XAxis type="number" tick={{ fill:'#6b7280', fontSize:11 }}/>
                  <YAxis type="category" dataKey="name" tick={{ fill:'#6b7280', fontSize:11 }} width={100}/>
                  <Tooltip contentStyle={tt}/>
                  <Bar dataKey="MAE" fill="#2563eb" radius={[0,4,4,0]} barSize={12} name="MAE"/>
                  <Bar dataKey="RMSE" fill="#ea580c" radius={[0,4,4,0]} barSize={12} name="RMSE"/>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-container">
              <div className="chart-title">Performance Radar</div>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={radarData}>
                  <PolarGrid stroke="rgba(107,112,128,0.08)"/>
                  <PolarAngleAxis dataKey="metric" tick={{ fill:'#6b7280', fontSize:11 }}/>
                  <PolarRadiusAxis tick={false} domain={[0,100]}/>
                  {rulEntries.map(([n],i)=>(
                    <Radar key={n} name={n} dataKey={n} stroke={colors[i]} fill={colors[i]} fillOpacity={0.15}/>
                  ))}
                  <Tooltip contentStyle={tt}/>
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Predicted vs Actual */}
          <div className="section fade-in stagger-4">
            <div className="chart-container">
              <div className="chart-title">Predicted vs Actual RUL</div>
              <div style={{ marginBottom:12 }}>
                <select className="form-select" value={currentModel} onChange={e=>setSelModel(e.target.value)}>
                  {rulEntries.map(([n])=><option key={n} value={n}>{n}</option>)}
                </select>
              </div>
              {scatterData.length > 0 && (
                <ResponsiveContainer width="100%" height={350}>
                  <ScatterChart>
                    <XAxis type="number" dataKey="actual" name="Actual" tick={{ fill:'#6b7280', fontSize:11 }} label={{ value:'Actual RUL', fill:'#6b7280', position:'bottom' }}/>
                    <YAxis type="number" dataKey="predicted" name="Predicted" tick={{ fill:'#6b7280', fontSize:11 }} label={{ value:'Predicted RUL', fill:'#6b7280', angle:-90, position:'left' }}/>
                    <ZAxis type="number" dataKey="error" range={[20,200]}/>
                    <Tooltip contentStyle={tt} formatter={(v,n)=>[v.toFixed(1),n]}/>
                    <Scatter data={scatterData} fill="#2563eb" opacity={0.5}/>
                  </ScatterChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </>}

        {tab === 'classification' && <>
          <div className="section fade-in stagger-1">
            <div className="chart-container">
              <div className="chart-title">Classification Performance</div>
              <table className="data-table">
                <thead><tr><th>Model</th><th>Accuracy</th><th>Precision</th><th>Recall</th><th>F1</th></tr></thead>
                <tbody>
                  {Object.entries(cls).map(([n,m])=>(
                    <tr key={n}>
                      <td style={{ fontWeight:600, color:'var(--cyan)' }}>{n}</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{(m.Accuracy*100).toFixed(2)}%</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{(m.Precision*100).toFixed(2)}%</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{(m.Recall*100).toFixed(2)}%</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{(m.F1*100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Confusion Matrices */}
          <div className="grid-2 section fade-in stagger-2">
            {Object.entries(clsMatrices).map(([n,cm])=>(
              <div key={n} className="chart-container">
                <div className="chart-title">{n} - Confusion Matrix</div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, maxWidth:280, margin:'0 auto' }}>
                  {[
                    { label:'TN', val:cm.TN, color:'var(--green)' },
                    { label:'FP', val:cm.FP, color:'var(--red)' },
                    { label:'FN', val:cm.FN, color:'var(--orange)' },
                    { label:'TP', val:cm.TP, color:'var(--cyan)' },
                  ].map(c=>(
                    <div key={c.label} style={{ background:'var(--bg-secondary)', borderRadius:8, padding:20, textAlign:'center' }}>
                      <div style={{ fontSize:'0.72rem', color:'var(--text-secondary)', marginBottom:4 }}>{c.label}</div>
                      <div style={{ fontFamily:'var(--font-heading)', fontSize:'1.5rem', color:c.color }}>{c.val}</div>
                    </div>
                  ))}
                </div>
                <div style={{ textAlign:'center', marginTop:12, fontSize:'0.72rem', color:'var(--text-muted)' }}>
                  Predicted →  |  ↓ Actual
                </div>
              </div>
            ))}
          </div>
        </>}
      </div>
    </>
  )
}
