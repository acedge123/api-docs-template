import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, Home, ArrowLeft, Search } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="container mx-auto px-4">
        <div className="max-w-2xl mx-auto text-center">
          <Card className="p-8">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <Zap className="h-16 w-16 text-blue-600" />
                  <Search className="h-8 w-8 text-gray-400 absolute -top-2 -right-2" />
                </div>
              </div>
              <CardTitle className="text-6xl font-bold text-gray-900 mb-4">404</CardTitle>
              <h2 className="text-2xl font-semibold text-gray-700 mb-4">Page Not Found</h2>
              <p className="text-gray-600 mb-8">
                Sorry, we couldn't find the page you're looking for. It might have been moved, 
                deleted, or you entered the wrong URL.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild>
                  <Link to="/">
                    <Home className="h-4 w-4 mr-2" />
                    Go Home
                  </Link>
                </Button>
                <Button variant="outline" asChild>
                  <Link to="/documentation">
                    <ArrowLeft className="h-4 w-4 mr-2" />
                    View Documentation
                  </Link>
                </Button>
              </div>
              
              <div className="pt-6 border-t">
                <p className="text-sm text-gray-500 mb-4">Looking for something specific?</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                  <Link to="/" className="text-blue-600 hover:text-blue-800 transition-colors">
                    Home
                  </Link>
                  <Link to="/documentation" className="text-blue-600 hover:text-blue-800 transition-colors">
                    Documentation
                  </Link>
                  <Link to="/login" className="text-blue-600 hover:text-blue-800 transition-colors">
                    Admin Login
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
