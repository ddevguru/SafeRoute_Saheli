import React, { createContext, useContext, useState, useEffect } from 'react';
import { adminApi, getAuthToken, setAuthToken, removeAuthToken } from '../api/adminApi';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [adminUser, setAdminUser] = useState(() => {
    const saved = localStorage.getItem('saheli_admin_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [token, setToken] = useState(getAuthToken());
  const [loading, setLoading] = useState(false);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const res = await adminApi.login(username, password);
      if (res.success && res.access_token) {
        setAuthToken(res.access_token);
        setToken(res.access_token);
        const userObj = res.admin || { username, role: res.role || 'ADMIN' };
        setAdminUser(userObj);
        localStorage.setItem('saheli_admin_user', JSON.stringify(userObj));
        return { success: true };
      }
      return { success: false, error: res.error || 'Authentication failed' };
    } catch (err) {
      return { success: false, error: err.message || 'Server connection error' };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    removeAuthToken();
    localStorage.removeItem('saheli_admin_user');
    setToken(null);
    setAdminUser(null);
  };

  return (
    <AuthContext.Provider value={{ adminUser, token, isAuthenticated: !!token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
