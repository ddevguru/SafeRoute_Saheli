import React from 'react';
import { Search, RefreshCw, Bell, Radio } from 'lucide-react';

export const Header = ({ onRefresh, isRefreshing = false }) => {
  return (
    <header className="admin-header">
      <div className="header-search">
        <Search size={18} className="header-search-icon" />
        <input 
          type="text" 
          placeholder="Search by incident ID, Saheli name, device MAC..." 
        />
      </div>

      <div className="header-actions">
        {/* Real-time telemetry status */}
        <div className="status-pill-live">
          <span className="status-dot-green"></span>
          <span>DISPATCH MESH ONLINE</span>
        </div>

        {/* Manual Refresh Trigger */}
        <button 
          className="btn btn-outline btn-sm" 
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh All Telemetry"
        >
          <RefreshCw size={15} className={isRefreshing ? 'animate-spin' : ''} />
          <span>Sync Now</span>
        </button>
      </div>
    </header>
  );
};
