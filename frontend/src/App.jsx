import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Activity, FlaskConical, Crosshair, ClipboardList, Gauge
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import KPIs from './pages/KPIs'
import Monitoring from './pages/Monitoring'
import IALab from './pages/IALab'
import Prognostic from './pages/Prognostic'
import Logs from './pages/Logs'

const navItems = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/kpis',        icon: Gauge,           label: 'KPI Center' },
  { to: '/monitoring',  icon: Activity,        label: 'Monitoring' },
  { to: '/ia-lab',      icon: FlaskConical,    label: 'IA Lab' },
  { to: '/prognostic',  icon: Crosshair,       label: 'Prognostic' },
  { to: '/logs',        icon: ClipboardList,    label: 'Logs' },
]

export default function App() {
  const location = useLocation()

  return (
    <div className="app-layout">
      {/* ---- Sidebar ---- */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h1>⚡ PREDMAINT AI</h1>
          <div className="sub">NASA C-MAPSS Turbofan</div>
          <div className="sub">ENSAM Meknès — 4ème Année IA</div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              <Icon className="icon" size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          v1.0 — Predictive Maintenance<br />© 2026 ENSAM Meknès
        </div>
      </aside>

      {/* ---- Main ---- */}
      <main className="main-content">
        <Routes>
          <Route path="/"           element={<Dashboard />} />
          <Route path="/kpis"       element={<KPIs />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/ia-lab"     element={<IALab />} />
          <Route path="/prognostic" element={<Prognostic />} />
          <Route path="/logs"       element={<Logs />} />
        </Routes>
      </main>
    </div>
  )
}
