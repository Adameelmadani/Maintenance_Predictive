import { Routes, Route, NavLink, useLocation } from 'react-router-dom'
import { useState } from 'react'
import {
  LayoutDashboard, Activity, FlaskConical, Crosshair, Gauge, Zap
} from 'lucide-react'
import Dashboard from './pages/Dashboard'
import KPIs from './pages/KPIs'
import Monitoring from './pages/Monitoring'
import IALab from './pages/IALab'
import Prognostic from './pages/Prognostic'

const navItems = [
  { to: '/',            icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/kpis',        icon: Gauge,           label: 'KPI Center' },
  { to: '/monitoring',  icon: Activity,        label: 'Monitoring' },
  { to: '/ia-lab',      icon: FlaskConical,    label: 'IA Lab' },
  { to: '/prognostic',  icon: Crosshair,       label: 'Prognostic' },
]

export default function App() {
  const location = useLocation()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="app-layout">
      {/* Mobile topbar */}
      <div className="mobile-topbar">
        <button
          className="mobile-menu-btn"
          aria-label="Toggle menu"
          aria-expanded={sidebarOpen}
          onClick={() => setSidebarOpen(o => !o)}
        >
          ☰
        </button>
        <div className="mobile-topbar-title">PREDMAINT AI</div>
      </div>
      {/* ---- Sidebar ---- */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-icon"><Zap size={24} /></div>
          <h1>PREDMAINT AI</h1>
          <div className="sub">NASA C-MAPSS Turbofan</div>
          <div className="sub">ENSAM Meknès - 4ème Année IA</div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon className="icon" size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          v1.0 - Predictive Maintenance<br />Prof. ZAKI Smail
        </div>
      </aside>
      {/* overlay for mobile when sidebar open */}
      <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)} />

      {/* ---- Main ---- */}
      <main className="main-content">
        <Routes>
          <Route path="/"           element={<Dashboard />} />
          <Route path="/kpis"       element={<KPIs />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/ia-lab"     element={<IALab />} />
          <Route path="/prognostic" element={<Prognostic />} />
        </Routes>
      </main>
    </div>
  )
}
