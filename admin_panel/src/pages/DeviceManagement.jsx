import React, { useState, useEffect } from 'react';
import { Cpu, Plus, BatteryCharging, Wifi, Video, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const DeviceManagement = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    device_id: '',
    device_type: 'ESP32_WEARABLE',
    device_secret: '',
    nickname: 'Saheli Wearable Band'
  });
  const [submitting, setSubmitting] = useState(false);

  const loadDevices = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getDevices();
      if (res.success) {
        setDevices(res.devices || []);
      }
    } catch (e) {
      console.warn('Device load error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

  const handleRegister = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await adminApi.registerDevice(formData);
      if (res.success) {
        setShowModal(false);
        setFormData({
          device_id: '',
          device_type: 'ESP32_WEARABLE',
          device_secret: '',
          nickname: 'Saheli Wearable Band'
        });
        loadDevices();
      } else {
        alert(res.error || 'Failed to register device');
      }
    } catch (err) {
      alert(err.message || 'Network error');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Hardware Fleet Management</h1>
          <p className="page-desc">Provision and monitor ESP32 wearable bands and dedicated ESP32-CAM optical modules</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-outline" onClick={loadDevices}>
            <RefreshCw size={16} />
            <span>Refresh Telemetry</span>
          </button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} />
            <span>Provision New Device</span>
          </button>
        </div>
      </div>

      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Hardware ID</th>
                <th>Device Category</th>
                <th>Nickname</th>
                <th>Connection Status</th>
                <th>Battery Level</th>
                <th>WiFi Signal</th>
                <th>Camera Sensor</th>
                <th>Firmware</th>
              </tr>
            </thead>
            <tbody>
              {devices.length === 0 ? (
                <tr>
                  <td colSpan="8" style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                    No devices registered yet. Click <strong>Provision New Device</strong> to add an ESP32.
                  </td>
                </tr>
              ) : (
                devices.map((d) => (
                  <tr key={d.id}>
                    <td>
                      <strong>{d.device_id}</strong>
                    </td>
                    <td>
                      <span className={`badge ${d.device_type === 'ESP32_CAM' ? 'badge-info' : 'badge-gold'}`}>
                        {d.device_type === 'ESP32_CAM' ? 'ESP32-CAM' : 'Wearable Band'}
                      </span>
                    </td>
                    <td>{d.nickname || 'Saheli Safety Band'}</td>
                    <td>
                      <span className={`badge ${d.status === 'ONLINE' ? 'badge-resolved' : 'badge-warning'}`}>
                        {d.status}
                      </span>
                    </td>
                    <td>
                      {d.battery_percent !== null && d.battery_percent !== undefined ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <BatteryCharging size={16} color="#10B981" />
                          <span>{d.battery_percent}% ({d.battery_voltage || 3.9}V)</span>
                        </div>
                      ) : (
                        <span style={{ color: '#94A3B8' }}>External USB</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Wifi size={16} color="#002350" />
                        <span>{d.wifi_rssi ? `${d.wifi_rssi} dBm` : '-64 dBm'}</span>
                      </div>
                    </td>
                    <td>
                      {d.device_type === 'ESP32_CAM' ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#10B981' }}>
                          <CheckCircle2 size={16} />
                          <span>OV2640 OK</span>
                        </div>
                      ) : (
                        <span style={{ color: '#94A3B8' }}>N/A (Wearable)</span>
                      )}
                    </td>
                    <td>v{d.firmware_version || '1.0.0'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Provisioning Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3 className="card-title">Provision New ESP32 Hardware</h3>
              <button onClick={() => setShowModal(false)} style={{ fontSize: '1.2rem', color: '#64748B' }}>✕</button>
            </div>
            <form onSubmit={handleRegister}>
              <div className="modal-body">
                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.80rem', fontWeight: '700', color: '#0F172A', marginBottom: '6px' }}>
                    Hardware Serial / Device ID
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.device_id}
                    onChange={(e) => setFormData({ ...formData, device_id: e.target.value.toUpperCase() })}
                    placeholder="e.g. SAHELI-WEARABLE-002 or SAHELI-CAM-002"
                    style={{ width: '100%' }}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.80rem', fontWeight: '700', color: '#0F172A', marginBottom: '6px' }}>
                    Device Architecture
                  </label>
                  <select
                    value={formData.device_type}
                    onChange={(e) => setFormData({ ...formData, device_type: e.target.value })}
                    style={{ width: '100%' }}
                  >
                    <option value="ESP32_WEARABLE">ESP32 All-in-One Wearable (Touch, Mic, MPU, GPS)</option>
                    <option value="ESP32_CAM">Dedicated ESP32-CAM Camera & Streaming Node</option>
                  </select>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.80rem', fontWeight: '700', color: '#0F172A', marginBottom: '6px' }}>
                    Device Pre-Shared Secret (HMAC)
                  </label>
                  <input
                    type="password"
                    required
                    value={formData.device_secret}
                    onChange={(e) => setFormData({ ...formData, device_secret: e.target.value })}
                    placeholder="Shared secret matching config.h"
                    style={{ width: '100%' }}
                  />
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <label style={{ display: 'block', fontSize: '0.80rem', fontWeight: '700', color: '#0F172A', marginBottom: '6px' }}>
                    Friendly Nickname
                  </label>
                  <input
                    type="text"
                    value={formData.nickname}
                    onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                    placeholder="e.g. Saheli Band Silver"
                    style={{ width: '100%' }}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" disabled={submitting} className="btn btn-primary">
                  {submitting ? 'Registering...' : 'Provision Hardware'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
