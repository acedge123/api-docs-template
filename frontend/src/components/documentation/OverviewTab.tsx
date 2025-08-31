import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, CheckCircle, BarChart3, Users } from 'lucide-react';

const OverviewTab = () => {
  const features = [
    { 
      name: 'Custom Scoring Models', 
      description: 'Create sophisticated scoring algorithms with custom formulas and weighted criteria.',
      icon: BarChart3,
      color: 'text-blue-600'
    },
    { 
      name: 'Lead Management', 
      description: 'Track leads, analyze responses, and generate actionable insights.',
      icon: Users,
      color: 'text-green-600'
    },
    { 
      name: 'Smart Recommendations', 
      description: 'AI-powered recommendations based on lead scores and behavior patterns.',
      icon: Zap,
      color: 'text-purple-600'
    },
    { 
      name: 'Real-time Analytics', 
      description: 'Live dashboards with comprehensive reporting and performance metrics.',
      icon: CheckCircle,
      color: 'text-orange-600'
    }
  ];

  return (
    <div className="space-y-8">
      {/* What is HFC Scoring Engine */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-blue-600" />
            What is the HFC Scoring Engine?
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-gray-600">
            The HFC Scoring Engine is a powerful API that helps businesses score and qualify leads 
            using custom algorithms and intelligent recommendations. It processes lead data through 
            sophisticated scoring models and returns actionable insights to optimize your lead qualification process.
          </p>
          
          <div className="grid md:grid-cols-2 gap-4 mt-6">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="text-center p-4 bg-gray-50 rounded-lg">
                  <IconComponent className={`h-8 w-8 ${feature.color} mx-auto mb-2`} />
                  <h3 className="font-semibold">{feature.name}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card>
        <CardHeader>
          <CardTitle>How It Works</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-4">
              <Badge variant="outline" className="mt-1">1</Badge>
              <div>
                <h4 className="font-semibold">Submit Lead Data</h4>
                <p className="text-gray-600">Send lead information and answers to questions via our REST API</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <Badge variant="outline" className="mt-1">2</Badge>
              <div>
                <h4 className="font-semibold">Process Through Models</h4>
                <p className="text-gray-600">Our algorithms calculate scores using custom formulas and weighted criteria</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <Badge variant="outline" className="mt-1">3</Badge>
              <div>
                <h4 className="font-semibold">Generate Insights</h4>
                <p className="text-gray-600">Receive scores, recommendations, and actionable insights for each lead</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Benefits */}
      <Card>
        <CardHeader>
          <CardTitle>Key Benefits</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">For Sales Teams</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Prioritize leads based on scoring</li>
                <li>• Focus on high-value prospects</li>
                <li>• Increase conversion rates</li>
                <li>• Reduce time spent on low-quality leads</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">For Marketing Teams</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Optimize lead generation campaigns</li>
                <li>• Understand lead quality patterns</li>
                <li>• Improve targeting strategies</li>
                <li>• Measure campaign effectiveness</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Start */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle>Quick Start</CardTitle>
          <CardDescription>
            Get up and running in 5 minutes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm mb-4">
            <div># Get your API key</div>
            <div className="text-gray-400">curl -X POST https://api.hfc-scoring.com/api/token-auth/ \</div>
            <div className="text-gray-400 ml-4">-H "Content-Type: application/json" \</div>
            <div className="text-gray-400 ml-4">-d '{"username": "your_username", "password": "your_password"}'</div>
            <div className="mt-2"># Submit a lead</div>
            <div className="text-gray-400">curl -X POST https://api.hfc-scoring.com/api/v1/leads/ \</div>
            <div className="text-gray-400 ml-4">-H "Authorization: Token YOUR_API_KEY" \</div>
            <div className="text-gray-400 ml-4">-H "Content-Type: application/json" \</div>
            <div className="text-gray-400 ml-4">-d '{"name": "John Doe", "email": "john@example.com", "answers": [...]}'</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default OverviewTab;
