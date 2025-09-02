import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Users, 
  BarChart3, 
  Settings, 
  FileText, 
  Target,
  TrendingUp,
  Database,
  Shield,
  Plus,
  ExternalLink
} from 'lucide-react';
import { Link } from 'react-router-dom';

// Admin Dashboard Component - HFC Scoring Engine Admin Interface
export default function Admin() {
  const adminSections = [
    {
      title: 'Questions',
      description: 'Create and manage scoring questions',
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      href: '/admin/scoringengine/question/',
      features: ['Question types', 'Field configuration', 'Choice options']
    },
    {
      title: 'Scoring Models',
      description: 'Configure X/Y axis scoring algorithms',
      icon: BarChart3,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      href: '/admin/scoringengine/scoringmodel/',
      features: ['Formula builder', 'Value ranges', 'Weight configuration']
    },
    {
      title: 'Recommendations',
      description: 'Set up rule-based recommendations',
      icon: Target,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      href: '/admin/scoringengine/recommendation/',
      features: ['Rule engine', 'Affiliate links', 'Response templates']
    },
    {
      title: 'Users & Tokens',
      description: 'Manage client accounts and API access',
      icon: Users,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      href: '/admin/auth/user/',
      features: ['Client accounts', 'API tokens', 'Access control']
    },
    {
      title: 'Lead Analytics',
      description: 'View lead data and scoring results',
      icon: TrendingUp,
      color: 'text-red-600',
      bgColor: 'bg-red-50',
      href: '/admin/scoringengine/lead/',
      features: ['Lead database', 'Score analytics', 'Export data']
    },
    {
      title: 'System Settings',
      description: 'Configure system preferences',
      icon: Settings,
      color: 'text-gray-600',
      bgColor: 'bg-gray-50',
      href: '/admin/',
      features: ['Site configuration', 'User permissions', 'System logs']
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-600 mr-2" />
              <h1 className="text-xl font-bold text-gray-900">Scoring Engine Admin</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" asChild>
                <Link to="/">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Back to Site
                </Link>
              </Button>
              <Button asChild>
                <a href="/admin/" target="_blank" rel="noopener noreferrer">
                  <Database className="mr-2 h-4 w-4" />
                  Django Admin
                </a>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Admin Dashboard
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Manage your scoring engine configuration, client accounts, and view analytics. 
            Use the sections below to access different admin functions.
          </p>
        </div>

        {/* Admin Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {adminSections.map((section) => {
            const IconComponent = section.icon;
            return (
              <Card key={section.title} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-lg ${section.bgColor}`}>
                      <IconComponent className={`h-6 w-6 ${section.color}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{section.title}</CardTitle>
                      <CardDescription className="text-sm">
                        {section.description}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <ul className="space-y-1">
                      {section.features.map((feature) => (
                        <li key={feature} className="text-sm text-gray-600 flex items-center">
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mr-2"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                    <Button asChild className="w-full mt-4">
                      <a href={section.href} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="mr-2 h-4 w-4" />
                        Open {section.title}
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks to get you started
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button asChild variant="outline">
                <a href="/admin/scoringengine/question/add/" target="_blank" rel="noopener noreferrer">
                  <Plus className="mr-2 h-4 w-4" />
                  Add New Question
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href="/admin/auth/user/add/" target="_blank" rel="noopener noreferrer">
                  <Users className="mr-2 h-4 w-4" />
                  Create Client Account
                </a>
              </Button>
              <Button asChild variant="outline">
                <a href="/admin/authtoken/token/add/" target="_blank" rel="noopener noreferrer">
                  <Shield className="mr-2 h-4 w-4" />
                  Generate API Token
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Help Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Getting Started</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">1</div>
                  <div>
                    <h4 className="font-medium">Create Questions</h4>
                    <p className="text-sm text-gray-600">Set up questions to gather lead information</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">2</div>
                  <div>
                    <h4 className="font-medium">Configure Scoring</h4>
                    <p className="text-sm text-gray-600">Set up X/Y axis scoring models</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">3</div>
                  <div>
                    <h4 className="font-medium">Add Recommendations</h4>
                    <p className="text-sm text-gray-600">Create rule-based recommendations</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">4</div>
                  <div>
                    <h4 className="font-medium">Create Client Accounts</h4>
                    <p className="text-sm text-gray-600">Set up users and generate API tokens</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-sm text-gray-600">
                  For technical support or questions about the scoring engine:
                </p>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center">
                    <ExternalLink className="mr-2 h-4 w-4 text-gray-400" />
                    <a href="/documentation" className="text-blue-600 hover:underline">View Documentation</a>
                  </li>
                  <li className="flex items-center">
                    <ExternalLink className="mr-2 h-4 w-4 text-gray-400" />
                    <a href="/admin/" className="text-blue-600 hover:underline">Django Admin Interface</a>
                  </li>
                  <li className="flex items-center">
                    <ExternalLink className="mr-2 h-4 w-4 text-gray-400" />
                    <span className="text-gray-600">Contact: admin@example.com</span>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
