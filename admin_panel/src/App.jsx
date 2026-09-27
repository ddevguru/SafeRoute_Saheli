import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { AdminLogin } from './pages/AdminLogin';
import { DashboardOverview } from './pages/DashboardOverview';
import { EmergencyDispatch } from './pages/EmergencyDispatch';
import { DeviceManagement } from './pages/DeviceManagement';
import { SafePlacesDirectory } from './pages/SafePlacesDirectory';
import { AIRiskAnalytics } from './pages/AIRiskAnalytics';
import { UsersDirectory } from './pages/UsersDirectory';
import { AuditLogs } from './pages/AuditLogs';

// Protected Layout Container
const ProtectedLayout = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [isRefreshing, setIsRefreshing] = useState(false);

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const handleGlobalRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      window.location.reload();
    }, 600);
  };

  return (
    <div className="admin-layout">
      <Sidebar activeEmergencyCount={1} />
      <div className="admin-main">
        <Header onRefresh={handleGlobalRefresh} isRefreshing={isRefreshing} />
        <main className="page-body">
          {children}
        </main>
      </div>
    </div>
  );
};

export const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<AdminLogin />} />

          <Route path="/dashboard" element={
            <ProtectedLayout>
              <DashboardOverview />
            </ProtectedLayout>
          } />

          <Route path="/emergencies" element={
            <ProtectedLayout>
              <EmergencyDispatch />
            </ProtectedLayout>
          } />

          <Route path="/devices" element={
            <ProtectedLayout>
              <DeviceManagement />
            </ProtectedLayout>
          } />

          <Route path="/safe-places" element={
            <ProtectedLayout>
              <SafePlacesDirectory />
            </ProtectedLayout>
          } />

          <Route path="/risk-analytics" element={
            <ProtectedLayout>
              <AIRiskAnalytics />
            </ProtectedLayout>
          } />

          <Route path="/users" element={
            <ProtectedLayout>
              <UsersDirectory />
            </ProtectedLayout>
          } />

          <Route path="/audit-logs" element={
            <ProtectedLayout>
              <AuditLogs />
            </ProtectedLayout>
          } />

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
