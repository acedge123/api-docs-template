import { Toaster } from '@/components/ui/toaster';
import { Toaster as Sonner } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Index from './pages/Index';
import Documentation from './pages/Documentation';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import NotFound from './pages/NotFound';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('authToken');
    setIsAuthenticated(!!token);
  }, []);

  if (isAuthenticated === null) {
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path='/' element={<Index />} />
          <Route path='/documentation' element={<Documentation />} />
          <Route path='/privacy-policy' element={<PrivacyPolicy />} />
          <Route path='/terms-of-service' element={<TermsOfService />} />
          <Route path='/login' element={<Login />} />
          
          {/* Protected Admin Routes */}
          <Route path='/dashboard' element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path='/questions' element={
            <ProtectedRoute>
              <div>Questions Management (Coming Soon)</div>
            </ProtectedRoute>
          } />
          <Route path='/scoring-models' element={
            <ProtectedRoute>
              <div>Scoring Models (Coming Soon)</div>
            </ProtectedRoute>
          } />
          <Route path='/recommendations' element={
            <ProtectedRoute>
              <div>Recommendations (Coming Soon)</div>
            </ProtectedRoute>
          } />
          <Route path='/analytics' element={
            <ProtectedRoute>
              <div>Analytics (Coming Soon)</div>
            </ProtectedRoute>
          } />
          <Route path='/settings' element={
            <ProtectedRoute>
              <div>Settings (Coming Soon)</div>
            </ProtectedRoute>
          } />
          
          {/* Catch all */}
          <Route path='*' element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
