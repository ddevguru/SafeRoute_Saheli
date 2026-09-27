/**
 * SafeRoute Saheli Admin API Client
 * Connects to Python Flask backend with JWT bearer token
 */

const BASE_URL = '/api';

export const getAuthToken = () => localStorage.getItem('saheli_admin_token');
export const setAuthToken = (token) => localStorage.setItem('saheli_admin_token', token);
export const removeAuthToken = () => localStorage.removeItem('saheli_admin_token');

const request = async (endpoint, options = {}) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers,
  };

  try {
    const res = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 401) {
      removeAuthToken();
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please log in again.');
    }

    const data = await res.json();
    return data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
};

export const adminApi = {
  // Authentication
  login: async (username, password) => {
    return request('/admin/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
  },

  // Dashboard Stats
  getDashboardMetrics: async () => {
    return request('/admin/dashboard');
  },

  // Emergencies
  getEmergencies: async (status = null) => {
    const query = status ? `?status=${status}` : '';
    return request(`/admin/emergencies${query}`);
  },

  resolveEmergency: async (incidentId, notes = 'Resolved by operator') => {
    return request(`/emergency/${incidentId}/resolve`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  },

  // Devices & Fleet
  getDevices: async () => {
    return request('/admin/devices');
  },

  registerDevice: async (deviceData) => {
    return request('/devices/register', {
      method: 'POST',
      body: JSON.stringify(deviceData),
    });
  },

  // Cameras & Evidence
  getCameras: async () => {
    return request('/admin/cameras');
  },

  getAudioEvidence: async () => {
    return request('/admin/audio');
  },

  // Safe Places & High Risk Zones
  getSafePlaces: async (category = null) => {
    const query = category ? `?category=${category}` : '';
    return request(`/nearby/safe-places${query}`);
  },

  getHighRiskZones: async () => {
    return request('/admin/high-risk-zones');
  },

  // AI & Risk Inference
  evaluateRisk: async (factors) => {
    return request('/ai/risk', {
      method: 'POST',
      body: JSON.stringify(factors),
    });
  },

  // Audit Logs
  getAuditLogs: async () => {
    return request('/admin/audit-logs');
  },

  // Users
  getUsers: async () => {
    return request('/admin/users');
  },

  // Forensics Chain of Custody & Merkle Engine
  getEvidenceChain: async (incidentId) => {
    return request(`/evidence/${incidentId}/chain`);
  },

  verifyEvidenceIntegrity: async (incidentId) => {
    return request(`/evidence/${incidentId}/verify-integrity`, {
      method: 'POST',
    });
  },

  getEvidenceCertificate: async (incidentId) => {
    return request(`/evidence/${incidentId}/certificate`);
  },

  // Geo-Fence Safe Zones & Battery Optimizer
  getSafeZones: async () => {
    return request('/geofence/zones');
  },

  createSafeZone: async (zoneData) => {
    return request('/geofence/zones', {
      method: 'POST',
      body: JSON.stringify(zoneData),
    });
  },

  checkGeofenceStatus: async (lat, lng) => {
    return request(`/geofence/check?lat=${lat}&lng=${lng}`);
  },
};

