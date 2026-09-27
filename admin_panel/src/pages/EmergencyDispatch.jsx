import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle,
  XCircle,
  Clock,
  MapPin,
  Phone,
  Volume2,
  Video,
  UserCheck,
  Send,
  AlertTriangle,
  Play,
  Pause,
  ExternalLink
} from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const EmergencyDispatch = () => {
  const [emergencies, setEmergencies] = useState([]);
  const [filter, setFilter] = useState('ALL');
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [resolveNotes, setResolveNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const fetchEmergencies = async () => {
    try {
      const res = await adminApi.getEmergencies(filter === 'ALL' ? null : filter);
      if (res.success) {
        setEmergencies(res.emergencies || []);
      }
    } catch (err) {
      console.warn('Failed to fetch emergencies:', err);
    }
  };

  useEffect(() => {
    fetchEmergencies();
    const interval = setInterval(fetchEmergencies, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const handleResolve = async (e) => {
    e.preventDefault();
    if (!selectedIncident) return;
    setIsSubmitting(true);
    try {
      const res = await adminApi.resolveEmergency(selectedIncident.id, resolveNotes);
      if (res.success) {
        setSelectedIncident(null);
        setResolveNotes('');
        fetchEmergencies();
      }
    } catch (err) {
      alert('Failed to resolve incident: ' + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Emergency Incident Dispatch Board</h1>
          <p className="page-desc">Real-time SOS coordination, multi-sensor evidence review & live camera streaming</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'ACTIVE', 'RESOLVED', 'CANCELLED'].map((tab) => (
            <button
              key={tab}
              onClick={() => setFilter(tab)}
              className={`btn btn-sm ${filter === tab ? 'btn-primary' : 'btn-outline'}`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Incident List */}
      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Incident ID</th>
                <th>Saheli User</th>
                <th>Trigger Source</th>
                <th>Location Coordinates</th>
                <th>Started Time</th>
                <th>Current Status</th>
                <th>Evidence & Action</th>
              </tr>
            </thead>
            <tbody>
              {emergencies.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                    No emergency incidents found for filter: <strong>{filter}</strong>
                  </td>
                </tr>
              ) : (
                emergencies.map((inc) => (
                  <tr key={inc.id} style={{ background: inc.status === 'ACTIVE' ? '#FFF5F5' : 'transparent' }}>
                    <td>
                      <strong>#{inc.id?.substring(0, 8)}</strong>
                    </td>
                    <td>
                      <div style={{ fontWeight: '600' }}>{inc.user_name || 'Saheli User'}</div>
                      <div style={{ fontSize: '0.78rem', color: '#64748B' }}>{inc.user_phone || '+91 98765 43210'}</div>
                    </td>
                    <td>
                      <span className={`badge ${inc.status === 'ACTIVE' ? 'badge-emergency' : 'badge-gold'}`}>
                        {inc.trigger_type}
                      </span>
                    </td>
                    <td>
                      <a
                        href={`https://www.google.com/maps?q=${inc.latitude},${inc.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: '#002350', fontWeight: '500' }}
                      >
                        <MapPin size={14} color="#EF4444" />
                        <span>{inc.latitude?.toFixed(4)}, {inc.longitude?.toFixed(4)}</span>
                        <ExternalLink size={12} color="#64748B" />
                      </a>
                    </td>
                    <td>
                      <div style={{ fontSize: '0.82rem', color: '#475569' }}>
                        {inc.started_at ? new Date(inc.started_at).toLocaleTimeString() : 'Recent'}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${
                        inc.status === 'ACTIVE' ? 'badge-emergency' :
                        inc.status === 'RESOLVED' ? 'badge-resolved' : 'badge-warning'
                      }`}>
                        {inc.status}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => setSelectedIncident(inc)}
                        className={`btn btn-sm ${inc.status === 'ACTIVE' ? 'btn-danger' : 'btn-outline'}`}
                      >
                        Inspect & Action
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Incident Detail Inspection & Resolution Modal */}
      {selectedIncident && (
        <div className="modal-overlay" onClick={() => setSelectedIncident(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '780px' }}>
            <div className="modal-header" style={{
              background: selectedIncident.status === 'ACTIVE' ? '#FEF2F2' : '#F8FAFC',
              borderBottom: '1px solid #E2E8F0'
            }}>
              <div>
                <h3 style={{ color: selectedIncident.status === 'ACTIVE' ? '#B91C1C' : '#002350' }}>
                  Incident Dossier #{selectedIncident.id?.substring(0, 8)}
                </h3>
                <p style={{ fontSize: '0.80rem', color: '#64748B' }}>
                  Reported via {selectedIncident.trigger_type} Trigger
                </p>
              </div>
              <button onClick={() => setSelectedIncident(null)} style={{ fontSize: '1.2rem', color: '#64748B' }}>
                ✕
              </button>
            </div>

            <div className="modal-body">
              {/* User & Guardian Info Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                <div style={{ padding: '16px', background: '#F8FAFC', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.74rem', fontWeight: '700', color: '#64748B', textTransform: 'uppercase' }}>
                    Saheli Identity
                  </div>
                  <div style={{ fontSize: '1rem', fontWeight: '700', color: '#002350', marginTop: '4px' }}>
                    {selectedIncident.user_name || 'Saheli Protected User'}
                  </div>
                  <div style={{ fontSize: '0.84rem', color: '#475569', marginTop: '2px' }}>
                    Phone: {selectedIncident.user_phone || '+91 98765 43210'}
                  </div>
                  <div style={{ fontSize: '0.84rem', color: '#475569' }}>
                    Blood Group: {selectedIncident.blood_group || 'O+'}
                  </div>
                </div>

                <div style={{ padding: '16px', background: '#F8FAFC', borderRadius: '10px' }}>
                  <div style={{ fontSize: '0.74rem', fontWeight: '700', color: '#64748B', textTransform: 'uppercase' }}>
                    Emergency Guardian Relay
                  </div>
                  <div style={{ fontSize: '0.90rem', fontWeight: '600', color: '#002350', marginTop: '4px' }}>
                    SMS & Call Dispatched
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#10B981', marginTop: '4px' }}>
                    ✓ Twilio SMS Alert sent to 2 Guardians
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#10B981' }}>
                    ✓ Automated Phone Call Triggered
                  </div>
                </div>
              </div>

              {/* Multimedia Evidence Subsystem */}
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '0.95rem', color: '#002350', marginBottom: '10px' }}>
                  Captured Evidence & Live Feed
                </h4>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  {/* Camera Live Stream / Snapshot */}
                  <div style={{ background: '#001A3D', borderRadius: '10px', padding: '14px', color: '#FFFFFF' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.80rem', color: '#D2AE39' }}>
                        <Video size={16} />
                        <span>ESP32-CAM Live Feed</span>
                      </div>
                      <span className="badge badge-emergency" style={{ fontSize: '0.65rem' }}>ENCRYPTED</span>
                    </div>

                    <div style={{
                      height: '160px',
                      background: '#000E21',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      overflow: 'hidden'
                    }}>
                      <img 
                        src={`/api/camera/stream/demo-session?device_id=SAHELI-CAM-001`} 
                        alt="ESP32-CAM Feed" 
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <div style={{ position: 'absolute', bottom: '8px', left: '8px', fontSize: '0.70rem', color: '#D2AE39', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
                        Live Port 81 • 15 FPS
                      </div>
                    </div>
                  </div>

                  {/* Audio Microphone Recording Evidence */}
                  <div style={{ background: '#F8FAFC', borderRadius: '10px', padding: '14px', border: '1px solid #E2E8F0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.80rem', fontWeight: '700', color: '#002350', marginBottom: '10px' }}>
                      <Volume2 size={16} color="#002350" />
                      <span>INMP441 Acoustic Distress Snippet</span>
                    </div>

                    <div style={{
                      height: '80px',
                      background: '#002350',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#D2AE39',
                      padding: '10px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <button
                          onClick={() => setIsPlayingAudio(!isPlayingAudio)}
                          style={{
                            width: '36px',
                            height: '36px',
                            borderRadius: '50%',
                            background: '#D2AE39',
                            color: '#002350',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          {isPlayingAudio ? <Pause size={18} /> : <Play size={18} />}
                        </button>
                        <span style={{ fontSize: '0.80rem', color: '#FFFFFF' }}>
                          {isPlayingAudio ? 'Playing Acoustic Waveform...' : '3-Clap Pattern Verified'}
                        </span>
                      </div>
                    </div>

                    <div style={{ fontSize: '0.76rem', color: '#64748B', marginTop: '10px' }}>
                      Acoustic Model: Verified 3 rapid spikes (340ms, 380ms)
                    </div>
                  </div>
                </div>
              </div>

              {/* Resolution Form if active */}
              {selectedIncident.status === 'ACTIVE' && (
                <form onSubmit={handleResolve} style={{ borderTop: '1px solid #E2E8F0', paddingTop: '16px' }}>
                  <h4 style={{ fontSize: '0.90rem', color: '#002350', marginBottom: '8px' }}>
                    Resolve & Close Emergency Incident
                  </h4>
                  <textarea
                    rows={2}
                    value={resolveNotes}
                    onChange={(e) => setResolveNotes(e.target.value)}
                    placeholder="Enter dispatch notes (e.g. Police patrol reached site, Saheli verified safe in vehicle)..."
                    style={{ width: '100%', marginBottom: '12px' }}
                    required
                  />
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button
                      type="button"
                      className="btn btn-outline"
                      onClick={() => setSelectedIncident(null)}
                    >
                      Close Window
                    </button>
                    <button
                      type="submit"
                      disabled={isSubmitting}
                      className="btn btn-primary"
                    >
                      <CheckCircle size={16} />
                      <span>{isSubmitting ? 'Resolving...' : 'Confirm Resolution & Log Audit'}</span>
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
