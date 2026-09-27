import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  ShieldAlert,
  Cpu,
  MapPin,
  BrainCircuit,
  History,
  Users,
  LogOut,
  ShieldCheck,
  Video
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = ({ activeEmergencyCount = 0 }) => {
  const { adminUser, logout } = useAuth();

  return (
    <aside className="admin-sidebar">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="brand-icon">
          <ShieldCheck size={22} color="#002350" />
        </div>
        <div>
          <div className="brand-title">SAFEROUTE</div>
          <div className="brand-subtitle">Saheli Operations</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Operations Center</div>

        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} />
          <span>Overview</span>
        </NavLink>

        <NavLink to="/emergencies" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <ShieldAlert size={18} />
          <span>Emergency Dispatch</span>
          {activeEmergencyCount > 0 && (
            <span className="nav-badge-danger">{activeEmergencyCount} SOS</span>
          )}
        </NavLink>

        <div className="nav-section-title">Hardware & Fleet</div>

        <NavLink to="/devices" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Cpu size={18} />
          <span>Wearables & CAMs</span>
        </NavLink>

        <div className="nav-section-title">AI & Soft Computing</div>

        <NavLink to="/risk-analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <BrainCircuit size={18} />
          <span>ANFIS Risk Engine</span>
        </NavLink>

        <NavLink to="/safe-places" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <MapPin size={18} />
          <span>Safe Havens Directory</span>
        </NavLink>

        <div className="nav-section-title">System & Security</div>

        <NavLink to="/users" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Users size={18} />
          <span>Registered Users</span>
        </NavLink>

        <NavLink to="/audit-logs" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <History size={18} />
          <span>Security Audit Trail</span>
        </NavLink>
      </nav>

      {/* Footer Profile & Logout */}
      <div className="sidebar-footer">
        <div className="user-badge">
          <div className="user-avatar">
            {adminUser?.username ? adminUser.username.substring(0, 2).toUpperCase() : 'AD'}
          </div>
          <div>
            <div className="user-name">{adminUser?.username || 'Admin Operator'}</div>
            <div className="user-role">{adminUser?.role || 'SUPERADMIN'}</div>
          </div>
        </div>
        <button onClick={logout} title="Sign Out" style={{ color: '#94A3B8', padding: '6px' }}>
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};
