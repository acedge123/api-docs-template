import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Zap, 
  Target, 
  BarChart3, 
  Users, 
  Shield, 
  TrendingUp,
  CheckCircle,
  ArrowRight
} from 'lucide-react';

const OverviewTab = () => {
  const features = [
    {
      icon: Target,
      title: "X/Y Axis Scoring",
      description: "Multi-dimensional scoring that evaluates leads across two axes for more nuanced qualification",
      color: "text-blue-600"
    },
    {
      icon: BarChart3,
      title: "Custom Formulas",
      description: "Build complex mathematical formulas to calculate scores based on lead responses",
      color: "text-green-600"
    },
    {
      icon: Users,
      title: "Lead Management",
      description: "Track every lead with complete response history, scores, and qualification status",
      color: "text-purple-600"
    },
    {
      icon: Shield,
      title: "Secure API",
      description: "Enterprise-grade security with token-based authentication and data encryption",
      color: "text-red-600"
    },
    {
      icon: TrendingUp,
      title: "Real-time Analytics",
      description: "Monitor lead quality trends, conversion rates, and scoring model performance",
      color: "text-orange-600"
    },
    {
      icon: Zap,
      title: "Smart Recommendations",
      description: "Automatically categorize leads and provide personalized outreach recommendations",
      color: "text-yellow-600"
    }
  ];

  const questionTypes = [
    { type: "Open", description: "Free text responses", useCase: "Job titles, company names" },
    { type: "Choices", description: "Single selection from options", useCase: "Company size, industry" },
    { type: "Multiple Choices", description: "Multiple selections allowed", useCase: "Technologies used, pain points" },
    { type: "Slider", description: "Numeric range input", useCase: "Budget ranges, timeline" },
    { type: "Integer", description: "Numeric input", useCase: "Team size, budget amount" },
    { type: "Date", description: "Date picker", useCase: "Project timeline, purchase date" }
  ];

  return (
    <div className="space-y-8">
      {/* Introduction */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">HFC Scoring Engine</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          A powerful lead qualification system that automatically scores and categorizes leads 
          based on their responses to custom questions, helping sales teams focus on high-value prospects.
        </p>
        <div className="flex justify-center space-x-4">
          <Badge variant="secondary" className="text-sm">
            <Shield className="mr-1 h-3 w-3" />
            Production Ready
          </Badge>
          <Badge variant="secondary" className="text-sm">
            <Zap className="mr-1 h-3 w-3" />
            Real-time Scoring
          </Badge>
          <Badge variant="secondary" className="text-sm">
            <Users className="mr-1 h-3 w-3" />
            Multi-tenant
          </Badge>
        </div>
      </div>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="mr-2 h-5 w-5" />
            How It Works
          </CardTitle>
          <CardDescription>
            Simple 3-step process to transform your lead qualification
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                <span className="text-xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="font-semibold">Ask Questions</h3>
              <p className="text-sm text-gray-600">
                Set up custom questions to gather information about job titles, company size, 
                budget, timeline, and other qualification criteria.
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <span className="text-xl font-bold text-green-600">2</span>
              </div>
              <h3 className="font-semibold">Score Automatically</h3>
              <p className="text-sm text-gray-600">
                Our algorithms evaluate responses using your custom scoring models and 
                assign X/Y axis scores based on lead quality and potential value.
              </p>
            </div>
            <div className="text-center space-y-3">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto">
                <span className="text-xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="font-semibold">Get Recommendations</h3>
              <p className="text-sm text-gray-600">
                Receive prioritized lead lists with specific recommendations for how 
                and when to reach out to each prospect.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="mr-2 h-5 w-5" />
            Key Features
          </CardTitle>
          <CardDescription>
            Everything you need to build, manage, and optimize your lead scoring system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => {
              const IconComponent = feature.icon;
              return (
                <div key={feature.title} className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <IconComponent className={`h-5 w-5 ${feature.color}`} />
                    <h3 className="font-semibold">{feature.title}</h3>
                  </div>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Question Types */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="mr-2 h-5 w-5" />
            Question Types
          </CardTitle>
          <CardDescription>
            Flexible question types to gather the information you need
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {questionTypes.map((question) => (
              <div key={question.type} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">{question.type}</h4>
                  <Badge variant="outline" className="text-xs">
                    {question.type}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{question.description}</p>
                <p className="text-xs text-gray-500">
                  <strong>Use case:</strong> {question.useCase}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Benefits */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Benefits
          </CardTitle>
          <CardDescription>
            Why leading sales teams choose our scoring engine
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-green-700">For Sales Teams</h4>
              <ul className="space-y-2">
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Focus on high-value prospects</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Reduce time spent on low-priority leads</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Improve conversion rates</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Get personalized outreach recommendations</span>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-blue-700">For Organizations</h4>
              <ul className="space-y-2">
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <span className="text-sm">Data-driven lead qualification</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <span className="text-sm">Scalable lead processing</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <span className="text-sm">Comprehensive analytics and reporting</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-blue-600 mt-0.5" />
                  <span className="text-sm">Multi-tenant architecture for agencies</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Getting Started */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <ArrowRight className="mr-2 h-5 w-5" />
            Getting Started
          </CardTitle>
          <CardDescription>
            Ready to transform your lead qualification process?
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-gray-600">
              The HFC Scoring Engine is designed to be easy to set up and use. 
              Whether you're a sales team looking to improve lead qualification or 
              an agency managing multiple clients, we have you covered.
            </p>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-semibold text-blue-900 mb-2">For Developers</h4>
                <p className="text-sm text-blue-800 mb-3">
                  Integrate our REST API into your existing systems and start scoring leads immediately.
                </p>
                <a href="#api-reference" className="text-blue-600 hover:underline text-sm font-medium">
                  View API Reference →
                </a>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-semibold text-green-900 mb-2">For Administrators</h4>
                <p className="text-sm text-green-800 mb-3">
                  Use our admin interface to set up questions, scoring models, and manage client accounts.
                </p>
                <a href="/admin" className="text-green-600 hover:underline text-sm font-medium">
                  Access Admin Panel →
                </a>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OverviewTab;
