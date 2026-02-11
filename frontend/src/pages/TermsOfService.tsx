import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap } from 'lucide-react';

const TermsOfService = () => {
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
              <CardTitle className="text-3xl">Terms of Service</CardTitle>
              <p className="text-gray-600">Last updated: August 30, 2024</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-3">1. Acceptance of Terms</h2>
                <p className="text-gray-600">
                  By accessing and using the HFC Scoring Engine ("Service"), you accept and agree to be bound by
                  the terms and provision of this agreement. If you do not agree to abide by the above,
                  please do not use this service.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">2. Description of Service</h2>
                <p className="text-gray-600 mb-4">
                  The HFC Scoring Engine provides lead scoring and recommendation services through a REST API.
                  The service includes:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Lead scoring algorithms and calculations</li>
                  <li>Custom formula evaluation</li>
                  <li>Recommendation generation</li>
                  <li>Analytics and reporting</li>
                  <li>API access and documentation</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">3. User Accounts</h2>
                <p className="text-gray-600 mb-4">
                  To access certain features of the Service, you must create an account. You are responsible for:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Maintaining the confidentiality of your account credentials</li>
                  <li>All activities that occur under your account</li>
                  <li>Providing accurate and complete information</li>
                  <li>Notifying us immediately of any unauthorized use</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">4. Acceptable Use</h2>
                <p className="text-gray-600 mb-4">
                  You agree not to use the Service to:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>Violate any applicable laws or regulations</li>
                  <li>Infringe on intellectual property rights</li>
                  <li>Transmit harmful, offensive, or inappropriate content</li>
                  <li>Attempt to gain unauthorized access to our systems</li>
                  <li>Interfere with the Service's operation</li>
                  <li>Submit false or misleading information</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">5. Data and Privacy</h2>
                <p className="text-gray-600 mb-4">
                  Your use of the Service is also governed by our Privacy Policy. You agree that:
                </p>
                <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
                  <li>You have the right to submit any data you provide</li>
                  <li>You will comply with applicable data protection laws</li>
                  <li>You will obtain necessary consents for data processing</li>
                  <li>You will not submit sensitive personal information without proper safeguards</li>
                </ul>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">6. Intellectual Property</h2>
                <p className="text-gray-600 mb-4">
                  The Service and its original content, features, and functionality are owned by HFC Scoring Engine
                  and are protected by international copyright, trademark, patent, trade secret, and other
                  intellectual property laws.
                </p>
                <p className="text-gray-600">
                  You retain ownership of any data you submit, but grant us a license to process and analyze
                  that data to provide our services.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">7. Service Availability</h2>
                <p className="text-gray-600">
                  We strive to maintain high availability but do not guarantee uninterrupted access to the Service.
                  We may perform maintenance, updates, or modifications that temporarily affect availability.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">8. Limitation of Liability</h2>
                <p className="text-gray-600">
                  In no event shall HFC Scoring Engine be liable for any indirect, incidental, special,
                  consequential, or punitive damages, including without limitation, loss of profits, data,
                  use, goodwill, or other intangible losses, resulting from your use of the Service.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">9. Termination</h2>
                <p className="text-gray-600">
                  We may terminate or suspend your account and access to the Service immediately, without prior
                  notice, for any reason, including breach of these Terms of Service.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">10. Changes to Terms</h2>
                <p className="text-gray-600">
                  We reserve the right to modify these terms at any time. We will notify users of any material
                  changes by posting the new Terms of Service on this page.
                </p>
              </div>

              <div>
                <h2 className="text-xl font-semibold mb-3">11. Contact Information</h2>
                <p className="text-gray-600">
                  If you have any questions about these Terms of Service, please contact us at
                  legal@hfc-scoring.com
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

export default TermsOfService;
