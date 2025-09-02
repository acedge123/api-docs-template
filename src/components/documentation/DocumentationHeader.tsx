import React from 'react';
import { Button } from '@/components/ui/button';
import { Zap, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const DocumentationHeader = () => {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center py-4 gap-4">
          <div className="flex items-center gap-4 w-full sm:w-auto">
            <Link to="/">
              <Button variant="ghost" size="sm" className="text-xs sm:text-sm">
                <ArrowLeft className="h-3 w-3 sm:h-4 sm:w-4 mr-1 sm:mr-2" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <Zap className="h-6 w-6 sm:h-8 sm:w-8 text-blue-600" />
              <h1 className="text-lg sm:text-2xl font-bold text-gray-900">HFC Scoring Engine API</h1>
            </div>
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto justify-end">
            <Link to="/login">
              <Button className="text-xs sm:text-sm px-3 sm:px-4">Get API Key</Button>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DocumentationHeader;
