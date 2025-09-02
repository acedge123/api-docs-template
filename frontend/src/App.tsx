import { Toaster } from './components/ui/toaster';
import { Toaster as Sonner } from './components/ui/sonner';
import { TooltipProvider } from './components/ui/tooltip';
import { Routes, Route } from 'react-router-dom';
import Index from './pages/Index';
import Documentation from './pages/Documentation';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';
import NotFound from './pages/NotFound';
import Login from './pages/Login';
import Admin from './pages/Admin';

const App = () => {
  console.log('App component rendering...');
  
  return (
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <Routes>
        {/* Public Routes */}
        <Route path='/' element={<Index />} />
        <Route path='/documentation' element={<Documentation />} />
        <Route path='/privacy-policy' element={<PrivacyPolicy />} />
        <Route path='/terms-of-service' element={<TermsOfService />} />
        <Route path='/login' element={<Login />} />
        <Route path='/admin' element={<Admin />} />
        
        {/* Catch all */}
        <Route path='*' element={<NotFound />} />
      </Routes>
    </TooltipProvider>
  );
};

export default App;
