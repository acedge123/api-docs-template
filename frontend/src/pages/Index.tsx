import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, Users, BarChart3, Shield, Target, TrendingUp, CheckCircle, Code, BookOpen, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo on the left */}
            <Link to="/" className="flex items-center">
              <Zap className="h-8 w-8 text-blue-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">HFC Scoring Engine</span>
            </Link>
            
            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <Link to="/documentation" className="text-gray-600 hover:text-gray-900">Documentation</Link>
              <Link to="/admin" className="text-gray-600 hover:text-gray-900">Admin</Link>
              <Button asChild>
                <Link to="/documentation">Get Started</Link>
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Logo and Brand Name */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <Zap className="h-12 w-12 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">HFC Scoring Engine</h1>
          </div>
          
          <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Transform Your Lead Qualification
            <span className="text-blue-600"> with Intelligent Scoring</span>
            <br />Stop Wasting Time on Low-Value Prospects
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Automatically score and qualify leads based on their answers to your questions. 
            Focus your sales team on high-value prospects while filtering out low-priority leads. 
            Boost conversion rates and maximize revenue with data-driven lead qualification.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/documentation">
              <Button size="lg" className="w-full sm:w-auto">
                <BookOpen className="mr-2 h-5 w-5" />
                View Documentation
              </Button>
            </Link>
            <Link to="/admin">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                <Shield className="mr-2 h-5 w-5" />
                Admin Access
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Use Case Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Perfect for Sales Teams Like Yours
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Real-world example: How Valer uses our scoring engine to focus on high-value hospital executives
            </p>
          </div>
          
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 mb-12">
            <div className="grid md:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">The Challenge</h3>
                <p className="text-gray-600 mb-4">
                  Valer's sales team was spending valuable time talking to low-ranking employees 
                  from small hospitals instead of focusing on C-level executives at large hospitals 
                  who have real decision-making power and bigger budgets.
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-red-500" />
                    <span className="text-sm text-gray-600">Wasted time on low-value prospects</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-red-500" />
                    <span className="text-sm text-gray-600">Missed opportunities with high-value leads</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-red-500" />
                    <span className="text-sm text-gray-600">Poor conversion rates</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">The Solution</h3>
                <p className="text-gray-600 mb-4">
                  Using our scoring engine, Valer now automatically qualifies leads based on:
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-green-500" />
                    <span className="text-sm text-gray-600">Job title and decision-making authority</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-green-500" />
                    <span className="text-sm text-gray-600">Hospital size and budget capacity</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="h-5 w-5 text-green-500" />
                    <span className="text-sm text-gray-600">Urgency and timeline for purchase</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Powerful Features for Lead Qualification
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to build, manage, and optimize your lead scoring system
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <BarChart3 className="h-8 w-8 text-blue-600 mb-2" />
                <CardTitle>X/Y Axis Scoring</CardTitle>
                <CardDescription>
                  Create sophisticated two-dimensional scoring models that evaluate multiple aspects of lead quality
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Target className="h-8 w-8 text-green-600 mb-2" />
                <CardTitle>Smart Recommendations</CardTitle>
                <CardDescription>
                  Automatically categorize leads into priority buckets with personalized outreach recommendations
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-8 w-8 text-purple-600 mb-2" />
                <CardTitle>Lead Management</CardTitle>
                <CardDescription>
                  Track every lead with complete response history, scores, and qualification status
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-8 w-8 text-orange-600 mb-2" />
                <CardTitle>Custom Formulas</CardTitle>
                <CardDescription>
                  Build complex scoring algorithms with weighted questions and mathematical formulas
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <TrendingUp className="h-8 w-8 text-yellow-600 mb-2" />
                <CardTitle>Real-time Analytics</CardTitle>
                <CardDescription>
                  Monitor lead quality trends, conversion rates, and scoring model performance
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="h-8 w-8 text-red-600 mb-2" />
                <CardTitle>Secure API</CardTitle>
                <CardDescription>
                  Enterprise-grade security with token-based authentication and data encryption
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              How Lead Scoring Works
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Simple 3-step process to transform your lead qualification
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Ask Questions</h3>
              <p className="text-gray-600">
                Set up custom questions to gather information about job titles, company size, 
                budget, timeline, and other qualification criteria.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Score Automatically</h3>
              <p className="text-gray-600">
                Our algorithms evaluate responses using your custom scoring models and 
                assign X/Y axis scores based on lead quality and potential value.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="text-xl font-semibold mb-3">Get Recommendations</h3>
              <p className="text-gray-600">
                Receive prioritized lead lists with specific recommendations for how 
                and when to reach out to each prospect.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* API Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Simple API Integration
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get started in minutes with our straightforward REST API
            </p>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-8 max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-xl font-semibold mb-4">Submit a Lead</h3>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                  <div>POST /api/v1/leads/</div>
                  <div className="text-gray-400 mt-2">{'{'}</div>
                  <div className="ml-4">"name": "John Smith",</div>
                  <div className="ml-4">"email": "john@hospital.com",</div>
                  <div className="ml-4">"answers": [</div>
                  <div className="ml-8">{'{'}</div>
                  <div className="ml-12">"question_id": 1,</div>
                  <div className="ml-12">"response_text": "CEO"</div>
                  <div className="ml-8">{'}'}</div>
                  <div className="ml-4">]</div>
                  <div>{'}'}</div>
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-4">Get Score & Recommendations</h3>
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                  <div>{'{'}</div>
                  <div className="ml-4">"total_score": 85,</div>
                  <div className="ml-4">"x_score": 42,</div>
                  <div className="ml-4">"y_score": 43,</div>
                  <div className="ml-4">"priority": "High",</div>
                  <div className="ml-4">"recommendation": "Call within 24 hours"</div>
                  <div>{'}'}</div>
                </div>
              </div>
            </div>
            
            <div className="text-center mt-8">
              <Button asChild>
                <Link to="/documentation">
                  <Code className="mr-2 h-4 w-4" />
                  View Full API Documentation
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Lead Qualification?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join sales teams like Valer who are already using our scoring engine to 
            focus on high-value prospects and boost their conversion rates
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" asChild>
              <Link to="/documentation">
                <BookOpen className="mr-2 h-4 w-4" />
                Read Documentation
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white hover:text-blue-600" asChild>
              <Link to="/admin">
                <Shield className="mr-2 h-4 w-4" />
                Access Admin Panel
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Zap className="h-6 w-6 text-blue-400" />
                <span className="text-xl font-bold">HFC Scoring Engine</span>
              </div>
              <p className="text-gray-400">
                Intelligent lead scoring and qualification engine for modern sales teams.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/documentation" className="hover:text-white transition-colors">Documentation</Link></li>
                <li><Link to="/admin" className="hover:text-white transition-colors">Admin Panel</Link></li>
                <li><Link to="/documentation" className="hover:text-white transition-colors">API Reference</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/documentation" className="hover:text-white transition-colors">Help Center</Link></li>
                <li><Link to="/documentation" className="hover:text-white transition-colors">API Status</Link></li>
                <li><Link to="/documentation" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/privacy-policy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms-of-service" className="hover:text-white transition-colors">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 HFC Scoring Engine. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
 