import { useState, useEffect, useCallback } from 'react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell, AreaChart, Area, ReferenceLine
} from 'recharts'
import { api } from '../api'

export default function Monitoring() {
  const [engineId, setEngineId] = useState(1)
  const [sensor, setSensor] = useState('')
  const [win, setWin] = useState(30)
  const [data, setData] = useState(null)
  const [engines, setEngines] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { api.getEngines().then(d => setEngines(d.engine_ids)).catch(() => {}) }, [])

  const fetchData = useCallback(() => {
    setLoading(true)
    api.getMonitoring(engineId, sensor || 'sensor_2', win)
      .then(d => { setData(d); if (!sensor && d.available_sensors?.length) setSensor(d.available_sensors[0]); setLoading(false) })
      .catch(() => setLoading(false))
  }, [engineId, sensor, win])

  useEffect(() => { fetchData() }, [fetchData])

  if (loading && !data) return <div className="loading-screen"><div className="spinner"/><div className="loading-text">Loading sensor data...</div></div>

  const signalData = data ? data.cycles.map((c, i) => ({
    cycle: c, raw: data.signal[i], mean: data.rolling_mean[i],
    upper: data.rolling_mean[i] + (data.rolling_std[i] || 0),
    lower: data.rolling_mean[i] - (data.rolling_std[i] || 0),
  })) : []

  const fftData = data ? data.fft.frequencies.map((f, i) => ({ freq: +f.toFixed(4), amp: data.fft.amplitudes[i] })) : []

  const tt = { background: '#182240', border: '1px solid rgba(0,212,255,0.2)', borderRadius: 8, color: '#e8f4fd' }

  return (
    <>
      <div className="page-header"><h1>📡 SIGNAL MONITORING</h1><p>Sensor Visualization — FFT — Anomaly Detection</p></div>
      <div className="page-body">
        <div style={{ display:'flex', gap:16, marginBottom:24, flexWrap:'wrap' }} className="fade-in">
          <div>
            <label style={{ fontSize:'0.72rem', color:'var(--text-secondary)', display:'block', marginBottom:4, textTransform:'uppercase', letterSpacing:1 }}>Engine</label>
            <select className="form-select" value={engineId} onChange={e=>setEngineId(+e.target.value)}>
              {engines.map(id=><option key={id} value={id}>EN{String(id).padStart(3,'0')}</option>)}
            </select>
          </div>
          <div>
            <label style={{ fontSize:'0.72rem', color:'var(--text-secondary)', display:'block', marginBottom:4, textTransform:'uppercase', letterSpacing:1 }}>Sensor</label>
            <select className="form-select" value={sensor} onChange={e=>setSensor(e.target.value)}>
              {(data?.available_sensors||[]).map(s=><option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label style={{ fontSize:'0.72rem', color:'var(--text-secondary)', display:'block', marginBottom:4, textTransform:'uppercase', letterSpacing:1 }}>Window</label>
            <select className="form-select" value={win} onChange={e=>setWin(+e.target.value)}>
              {[5,10,20,30,50].map(w=><option key={w} value={w}>{w} cycles</option>)}
            </select>
          </div>
        </div>

        {data && <>
          <div className="kpi-grid fade-in stagger-1">
            {[
              { label:'RMS', val:data.stats.rms, accent:'cyan', icon:'📈' },
              { label:'Kurtosis', val:data.stats.kurtosis, accent:'orange', icon:'📊' },
              { label:'Peak-to-Peak', val:data.stats.peak_to_peak, accent:'purple', icon:'📏' },
              { label:'Skewness', val:data.stats.skewness, accent:'green', icon:'📐' },
            ].map(k=>(
              <div key={k.label} className={`kpi-card accent-${k.accent}`}>
                <div className="kpi-header"><span className="kpi-label">{k.label}</span><span className={`kpi-icon ${k.accent}`}>{k.icon}</span></div>
                <div className="kpi-value" style={{ fontSize:'1.4rem' }}>{k.val}</div>
              </div>
            ))}
          </div>

          <div className="section fade-in stagger-2">
            <div className="chart-container">
              <div className="chart-title">Raw Signal — {sensor} (Engine {engineId})</div>
              <ResponsiveContainer width="100%" height={340}>
                <AreaChart data={signalData}>
                  <XAxis dataKey="cycle" tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                  <YAxis tick={{ fill:'#7e8fa6', fontSize:11 }}/>
                  <Tooltip contentStyle={tt}/>
                  <Area type="monotone" dataKey="upper" stroke="none" fill="rgba(123,47,190,0.1)"/>
                  <Line type="monotone" dataKey="raw" stroke="#00d4ff" strokeWidth={1.5} dot={false} opacity={0.7}/>
                  <Line type="monotone" dataKey="mean" stroke="#00ff88" strokeWidth={2} dot={false} strokeDasharray="6 3"/>
                  {data.rul_threshold_cycle && <ReferenceLine x={data.rul_threshold_cycle} stroke="#ff3366" strokeDasharray="4 4"/>}
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="section fade-in stagger-3">
            <div className="chart-container">
              <div className="chart-title">FFT Spectrum — {sensor}</div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={fftData}>
                  <XAxis dataKey="freq" tick={{ fill:'#7e8fa6', fontSize:10 }}/>
                  <YAxis tick={{ fill:'#7e8fa6', fontSize:10 }}/>
                  <Tooltip contentStyle={tt}/>
                  <Bar dataKey="amp" radius={[4,4,0,0]}>
                    {fftData.map((_,i)=><Cell key={i} fill={`hsl(${180+i*4},80%,55%)`}/>)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="section fade-in stagger-4">
            <div className="chart-container">
              <div className="chart-title">Top Dominant Frequencies</div>
              <table className="data-table">
                <thead><tr><th>#</th><th>Frequency (Hz)</th><th>Amplitude</th></tr></thead>
                <tbody>
                  {data.fft.top_freqs.slice(0,8).map((f,i)=>(
                    <tr key={i}>
                      <td>{i+1}</td>
                      <td style={{ fontFamily:'var(--font-mono)', color:'var(--cyan)' }}>{f.toFixed(4)}</td>
                      <td style={{ fontFamily:'var(--font-mono)' }}>{data.fft.top_amps[i].toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>}
      </div>
    </>
  )
}
