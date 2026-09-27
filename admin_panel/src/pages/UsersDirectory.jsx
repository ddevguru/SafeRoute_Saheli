import React, { useState, useEffect } from 'react';
import { Users, ShieldCheck, Phone, Mail, Calendar, RefreshCw } from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const UsersDirectory = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getUsers();
      if (res.success) {
        setUsers(res.users || []);
      }
    } catch (e) {
      console.warn('Users load error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Registered Saheli Users Directory</h1>
          <p className="page-desc">Profiles and emergency configurations of women protected by SafeRoute Saheli</p>
        </div>
        <button className="btn btn-outline" onClick={loadUsers}>
          <RefreshCw size={16} />
          <span>Refresh Directory</span>
        </button>
      </div>

      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Saheli Full Name</th>
                <th>Contact Details</th>
                <th>Blood Group</th>
                <th>Guardian Camera Permission</th>
                <th>Account Status</th>
                <th>Registration Date</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                    No users retrieved from database.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{
                          width: '32px',
                          height: '32px',
                          borderRadius: '50%',
                          background: 'rgba(0, 35, 80, 0.1)',
                          color: '#002350',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontWeight: '700',
                          fontSize: '0.80rem'
                        }}>
                          {u.name ? u.name.substring(0, 2).toUpperCase() : 'SH'}
                        </div>
                        <div>
                          <div style={{ fontWeight: '600' }}>{u.name}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>ID: {u.id?.substring(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div style={{ fontSize: '0.82rem' }}>
                        <div>{u.phone}</div>
                        <div style={{ color: '#64748B' }}>{u.email}</div>
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-gold">{u.emergency_blood_group || 'O+'}</span>
                    </td>
                    <td>
                      {u.privacy_guardian_camera ? (
                        <span className="badge badge-resolved">ENABLED</span>
                      ) : (
                        <span className="badge badge-warning">EMERGENCY ONLY</span>
                      )}
                    </td>
                    <td>
                      <span className="badge badge-resolved">ACTIVE</span>
                    </td>
                    <td>
                      <span style={{ fontSize: '0.80rem', color: '#64748B' }}>
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'Active'}
                      </span>
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
