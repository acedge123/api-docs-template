import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Code, Copy, ExternalLink } from 'lucide-react';

const ApiReferenceTab = () => {
  const endpoints = [
    {
      method: 'POST',
      path: '/api/v1/leads/',
      description: 'Submit a new lead for scoring with automatic X/Y axis calculation',
      auth: 'Token required',
      status: 'active'
    },
    {
      method: 'GET',
      path: '/api/v1/leads/',
      description: 'Retrieve leads with filtering options',
      auth: 'Token required',
      status: 'active'
    },
    {
      method: 'GET',
      path: '/api/v1/leads/{id}/',
      description: 'Get detailed lead information with scores and recommendations',
      auth: 'Token required',
      status: 'active'
    },
    {
      method: 'POST',
      path: '/api/v1/questions/',
      description: 'Create custom questions',
      auth: 'Admin token required',
      status: 'active'
    },
    {
      method: 'GET',
      path: '/api/v1/questions/',
      description: 'List available questions',
      auth: 'Token required',
      status: 'active'
    },
    {
      method: 'POST',
      path: '/api/v1/scoring-models/',
      description: 'Create scoring models with formulas',
      auth: 'Admin token required',
      status: 'active'
    },
    {
      method: 'POST',
      path: '/api/v1/recommendations/',
      description: 'Create recommendation rules (supports calculated scores)',
      auth: 'Admin token required',
      status: 'active'
    }
  ];

  const exampleRequest = `curl -X POST https://api-docs-template-production.up.railway.app/api/v1/leads/ \\
  -H "Authorization: Token YOUR_API_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "lead_id": "test-lead-001",
    "answers": {
      "income": "60000",
      "credit_score": "750",
      "employment_years": "3"
    }
  }'`;

  const exampleResponse = `{
  "lead_id": "test-lead-001",
  "x_axis": 25.5,
  "y_axis": 18.2,
  "total_score": 43.7,
  "timestamp": "2024-01-15T10:30:00Z",
  "answers": [
    {
      "field_name": "income",
      "response": "60000",
      "points": 15.0
    },
    {
      "field_name": "credit_score", 
      "response": "750",
      "points": 10.5
    },
    {
      "field_name": "employment_years",
      "response": "3",
      "points": 8.0
    }
  ],
  "recommendations": [
    {
      "response_text": "High credit score and stable employment. Recommend premium product.",
      "redirect_url": "https://example.com/premium-offer"
    }
  ]
}`;

  return (
    <div className="space-y-8">
      {/* API Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Code className="mr-2 h-5 w-5" />
            API Reference
          </CardTitle>
          <CardDescription>
            Complete API documentation for integrating with the HFC Scoring Engine
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Base URL</h4>
              <code className="text-blue-800 font-mono">https://api-docs-template-production.up.railway.app</code>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2">Authentication</h4>
              <p className="text-green-800 text-sm">
                All API requests require a valid token in the Authorization header: 
                <code className="font-mono ml-1">Authorization: Token YOUR_API_TOKEN</code>
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-900 mb-2">🎯 Calculated Scores Feature</h4>
              <p className="text-purple-800 text-sm">
                The API automatically calculates X-axis, Y-axis, and total scores based on your scoring models. 
                These calculated scores can be used in recommendation rules: 
                <code className="font-mono ml-1">{`{x_axis_score}, {y_axis_score}, {total_score}`}</code>
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Endpoints */}
      <Card>
        <CardHeader>
          <CardTitle>Available Endpoints</CardTitle>
          <CardDescription>
            All available API endpoints with their methods and requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {endpoints.map((endpoint, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Badge 
                      variant={endpoint.method === 'GET' ? 'secondary' : 'default'}
                      className="font-mono"
                    >
                      {endpoint.method}
                    </Badge>
                    <code className="font-mono text-sm">{endpoint.path}</code>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {endpoint.status}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{endpoint.description}</p>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">Auth:</span>
                  <Badge variant="outline" className="text-xs">
                    {endpoint.auth}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Example Request */}
      <Card>
        <CardHeader>
          <CardTitle>Example Request</CardTitle>
          <CardDescription>
            Submit a lead for scoring with sample data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
              <pre className="whitespace-pre-wrap">{exampleRequest}</pre>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              <Copy className="mr-2 h-4 w-4" />
              Copy Example
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Example Response */}
      <Card>
        <CardHeader>
          <CardTitle>Example Response</CardTitle>
          <CardDescription>
            Sample response with scoring results and recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
              <pre className="whitespace-pre-wrap">{exampleResponse}</pre>
            </div>
            <Button variant="outline" size="sm" className="w-full">
              <Copy className="mr-2 h-4 w-4" />
              Copy Response
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* SDKs and Libraries */}
      <Card>
        <CardHeader>
          <CardTitle>SDKs & Libraries</CardTitle>
          <CardDescription>
            Official and community libraries for easy integration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2">JavaScript/Node.js</h4>
              <p className="text-sm text-gray-600 mb-3">
                Official SDK for Node.js and browser environments
              </p>
              <Button size="sm" variant="outline">
                <ExternalLink className="mr-2 h-4 w-4" />
                View on NPM
              </Button>
            </div>
            <div className="border rounded-lg p-4">
              <h4 className="font-semibold mb-2">Python</h4>
              <p className="text-sm text-gray-600 mb-3">
                Python client library for easy integration
              </p>
              <Button size="sm" variant="outline">
                <ExternalLink className="mr-2 h-4 w-4" />
                View on PyPI
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ApiReferenceTab;
