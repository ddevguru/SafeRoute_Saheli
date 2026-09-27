import React, { useState, useEffect } from 'react';
import { MapPin, Phone, ShieldCheck, Plus, CheckCircle, Cross, ExternalLink } from 'lucide-react';
import { adminApi } from '../api/adminApi';

export const SafePlacesDirectory = () => {
  const [places, setPlaces] = useState([]);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const loadPlaces = async () => {
    setLoading(true);
    try {
      const res = await adminApi.getSafePlaces(categoryFilter === 'ALL' ? null : categoryFilter);
      if (res.success) {
        setPlaces(res.places || []);
      }
    } catch (e) {
      console.warn('Safe places error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlaces();
  }, [categoryFilter]);

  return (
    <div className="animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Safe Havens & Emergency Directory</h1>
          <p className="page-desc">Verified physical sanctuaries integrated into the Genetic Safe Routing algorithm</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['ALL', 'POLICE', 'HOSPITAL', 'PHARMACY', 'SHELTER'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`btn btn-sm ${categoryFilter === cat ? 'btn-primary' : 'btn-outline'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Place Name</th>
                <th>Category</th>
                <th>Address</th>
                <th>Emergency Helpline</th>
                <th>24x7 Availability</th>
                <th>Verification</th>
                <th>Map View</th>
              </tr>
            </thead>
            <tbody>
              {places.length === 0 ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '36px', color: '#64748B' }}>
                    No places found for category: <strong>{categoryFilter}</strong>
                  </td>
                </tr>
              ) : (
                places.map((p) => (
                  <tr key={p.id}>
                    <td>
                      <div style={{ fontWeight: '600' }}>{p.name}</div>
                    </td>
                    <td>
                      <span className={`badge ${
                        p.category === 'POLICE' ? 'badge-primary' :
                        p.category === 'HOSPITAL' ? 'badge-emergency' : 'badge-gold'
                      }`}>
                        {p.category}
                      </span>
                    </td>
                    <td>{p.address}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Phone size={14} color="#002350" />
                        <span>{p.phone_number || '+91 112'}</span>
                      </div>
                    </td>
                    <td>
                      {p.is_24x7 ? (
                        <span className="badge badge-resolved">24x7 OPEN</span>
                      ) : (
                        <span className="badge badge-warning">DAY HOURS</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#10B981', fontSize: '0.80rem', fontWeight: '600' }}>
                        <ShieldCheck size={16} />
                        <span>VERIFIED</span>
                      </div>
                    </td>
                    <td>
                      <a
                        href={`https://www.google.com/maps?q=${p.latitude},${p.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                        className="btn btn-outline btn-sm"
                      >
                        <MapPin size={13} color="#EF4444" />
                        <span>View</span>
                      </a>
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
