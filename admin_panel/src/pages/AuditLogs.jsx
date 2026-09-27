import React, { useState, useEffect } from 'react';
import { History, Shield, Lock, User, RefreshCw } from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const AuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getAuditLogs();
      if (res.success) {
        setLogs(res.audit_logs || []);
      }
    } catch (e) {
      console.warn('Audit logs error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Security & Operations Audit Trail</h1>
          <p className="page-desc">Immutable chronological log of all operator interventions, camera access, and device pairings</p>
        </div>
        <button className="btn btn-outline" onClick={fetchLogs}>
          <RefreshCw size={16} />
          <span>Refresh Audit Trail</span>
        </button>
      </div>

      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Log Timestamp</th>
                <th>Actor Type</th>
                <th>Security Action</th>
                <th>Resource Target</th>
                <th>Metadata Payload</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                    No audit logs recorded yet.
                  </td>
                </tr>
              ) : (
                logs.map((l) => (
                  <tr key={l.id}>
                    <td>
                      <span style={{ fontSize: '0.82rem', color: '#64748B' }}>
                        {l.created_at ? new Date(l.created_at).toLocaleString() : 'Recent'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${l.actor_type === 'ADMIN' ? 'badge-primary' : 'badge-gold'}`}>
                        {l.actor_type}
                      </span>
                    </td>
                    <td>
                      <strong>{l.action}</strong>
                    </td>
                    <td>{l.resource || 'system'} #{l.resource_id || ''}</td>
                    <td>
                      <code style={{ fontSize: '0.78rem', background: '#F1F5F9', padding: '4px 8px', borderRadius: '4px' }}>
                        {l.details ? JSON.stringify(l.details) : '{}'}
                      </code>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
