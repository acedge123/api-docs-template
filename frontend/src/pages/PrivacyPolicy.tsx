import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap } from 'lucide-react';

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-blue-600" />
            <h1 className="text-2xl font-bold text-gray-900">HFC Scoring Engine</h1>
          </div>
          <nav className="flex items-center space-x-6">
            <Link to="/" className="text-gray-600 hover:text-gray-900 transition-colors">
              Home
            </Link>
            <Link to="/documentation" className="text-gray-600 hover:text-gray-900 transition-colors">
              Documentation
            </Link>
            <Link to="/login" className="text-gray-600 hover:text-gray-900 transition-colors">
              Admin Login
            </Link>
          </nav>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardHeader>
              <CardTitle className="text-3xl">Privacy Policy</CardTitle>
              <p className="text-gray-600">Last updated: August 30, 2024</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-3">1. Information We Collect</h2>
                <p className="text-gray-600 mb-4">
                  We collect information you provide directly to us, such as when you create an account,
                  submit leads for scoring, or contact us for support.
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Account information (username, email, password)</li>
                  <li>Lead data submitted for scoring (names, emails, responses)</li>
                  <li>Usage data and analytics</li>
                  <li>Communication records</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">2. How We Use Your Information</h2>
                <p className="text-gray-600 mb-4">
                  We use the information we collect to provide, maintain, and improve our services:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Process lead scoring requests</li>
                  <li>Generate recommendations and insights</li>
                  <li>Provide customer support</li>
                  <li>Improve our algorithms and services</li>
                  <li>Send important updates and notifications</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">3. Data Security</h2>
                <p className="text-gray-600 mb-4">
                  We implement appropriate security measures to protect your data:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Encryption of data in transit and at rest</li>
                  <li>Secure API authentication</li>
                  <li>Regular security audits</li>
                  <li>Access controls and monitoring</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">4. Data Sharing</h2>
                <p className="text-gray-600 mb-4">
                  We do not sell, trade, or otherwise transfer your personal information to third parties
                  except in the following circumstances:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>With your explicit consent</li>
                  <li>To comply with legal obligations</li>
                  <li>To protect our rights and safety</li>
                  <li>With service providers who assist in our operations</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">5. Your Rights</h2>
                <p className="text-gray-600 mb-4">
                  You have the right to:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Access your personal data</li>
                  <li>Correct inaccurate information</li>
                  <li>Request deletion of your data</li>
                  <li>Opt out of marketing communications</li>
                  <li>Export your data</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">6. Data Retention</h2>
                <p className="text-gray-600">
                  We retain your data for as long as necessary to provide our services and comply with
                  legal obligations. Lead data is typically retained for 2 years unless you request deletion.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">7. Contact Us</h2>
                <p className="text-gray-600">
                  If you have any questions about this Privacy Policy or our data practices,
                  please contact us at privacy@hfc-scoring.com
                </p>
              </div>

              <div className="pt-6 border-t">
                <Button asChild>
                  <Link to="/">Back to Home</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;
