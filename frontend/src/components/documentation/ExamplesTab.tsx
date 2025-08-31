import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Code, Copy, ExternalLink, CheckCircle } from 'lucide-react';

const ExamplesTab = () => {
  const examples = [
    {
      title: 'Hospital Executive Lead',
      description: 'High-value CTO from large hospital system',
      score: 'X: 95, Y: 88',
      status: 'High Priority',
      color: 'green',
      data: {
        name: 'Dr. Sarah Johnson',
        title: 'Chief Technology Officer',
        company: 'Metro Health Systems',
        employees: '5000+',
        budget: '$500k-1M',
        timeline: '1-3 months'
      }
    },
    {
      title: 'Startup Founder',
      description: 'Early-stage startup with limited budget',
      score: 'X: 70, Y: 45',
      status: 'Medium Priority',
      color: 'blue',
      data: {
        name: 'Alex Chen',
        title: 'Founder & CEO',
        company: 'TechStart Inc',
        employees: '10-50',
        budget: '$50k-100k',
        timeline: '3-6 months'
      }
    },
    {
      title: 'Enterprise Manager',
      description: 'Mid-level manager at Fortune 500',
      score: 'X: 60, Y: 75',
      status: 'Medium Priority',
      color: 'blue',
      data: {
        name: 'Michael Rodriguez',
        title: 'IT Manager',
        company: 'Global Corp',
        employees: '1000+',
        budget: '$100k-500k',
        timeline: 'Immediate'
      }
    }
  ];

  const codeExamples = [
    {
      language: 'JavaScript',
      title: 'Node.js Integration',
      code: `const axios = require('axios');

const submitLead = async (leadData) => {
  try {
    const response = await axios.post(
      'https://api.hfc-scoring.com/api/v1/leads/',
      leadData,
      {
        headers: {
          'Authorization': 'Token YOUR_API_TOKEN',
          'Content-Type': 'application/json'
        }
      }
    );
    
    console.log('Lead scored:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error submitting lead:', error);
  }
};

// Example usage
const leadData = {
  name: 'John Doe',
  email: 'john@example.com',
  company: 'Acme Corp',
  answers: [
    { question_id: 1, response: 'CTO' },
    { question_id: 2, response: '500-1000' },
    { question_id: 3, response: '100000-500000' }
  ]
};

submitLead(leadData);`
    },
    {
      language: 'Python',
      title: 'Python Integration',
      code: `import requests

def submit_lead(lead_data):
    url = 'https://api.hfc-scoring.com/api/v1/leads/'
    headers = {
        'Authorization': 'Token YOUR_API_TOKEN',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, json=lead_data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print(f"Lead scored: {result}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error submitting lead: {e}")

# Example usage
lead_data = {
    'name': 'Jane Smith',
    'email': 'jane@example.com',
    'company': 'Tech Solutions',
    'answers': [
        {'question_id': 1, 'response': 'CEO'},
        {'question_id': 2, 'response': '100-499'},
        {'question_id': 3, 'response': '50000-100000'}
    ]
}

submit_lead(lead_data)`
    },
    {
      language: 'cURL',
      title: 'Direct API Call',
      code: `# Submit a new lead
curl -X POST https://api.hfc-scoring.com/api/v1/leads/ \\
  -H "Authorization: Token YOUR_API_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Bob Wilson",
    "email": "bob@startup.com",
    "company": "Innovation Labs",
    "answers": [
      {
        "question_id": 1,
        "response": "Founder"
      },
      {
        "question_id": 2,
        "response": "10-50"
      },
      {
        "question_id": 3,
        "response": "10000-50000"
      }
    ]
  }'

# Get lead details
curl -X GET https://api.hfc-scoring.com/api/v1/leads/123/ \\
  -H "Authorization: Token YOUR_API_TOKEN"`,
      description: 'Direct API calls using cURL'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Real Examples */}
      <Card>
        <CardHeader>
          <CardTitle>Real Lead Examples</CardTitle>
          <CardDescription>
            See how different types of leads are scored and categorized
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {examples.map((example, index) => (
              <div key={index} className="border rounded-lg p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{example.title}</h3>
                    <p className="text-gray-600">{example.description}</p>
                  </div>
                  <div className="text-right">
                    <Badge 
                      variant={example.color === 'green' ? 'default' : 'secondary'}
                      className="mb-2"
                    >
                      {example.status}
                    </Badge>
                    <div className="text-sm font-mono text-gray-600">
                      {example.score}
                    </div>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Name</span>
                    <div className="font-medium">{example.data.name}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Title</span>
                    <div className="font-medium">{example.data.title}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Company</span>
                    <div className="font-medium">{example.data.company}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Company Size</span>
                    <div className="font-medium">{example.data.employees}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Budget</span>
                    <div className="font-medium">{example.data.budget}</div>
                  </div>
                  <div className="bg-gray-50 p-3 rounded">
                    <span className="text-xs text-gray-500">Timeline</span>
                    <div className="font-medium">{example.data.timeline}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Code Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Code className="mr-2 h-5 w-5" />
            Integration Examples
          </CardTitle>
          <CardDescription>
            Code examples for integrating with the HFC Scoring Engine API
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {codeExamples.map((codeExample, index) => (
              <div key={index} className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">{codeExample.title}</h4>
                  <Badge variant="outline">{codeExample.language}</Badge>
                </div>
                {codeExample.description && (
                  <p className="text-sm text-gray-600">{codeExample.description}</p>
                )}
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm">
                  <pre className="whitespace-pre-wrap">{codeExample.code}</pre>
                </div>
                <Button variant="outline" size="sm" className="w-full">
                  <Copy className="mr-2 h-4 w-4" />
                  Copy Code
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle>Best Practices</CardTitle>
          <CardDescription>
            Tips for getting the most out of the HFC Scoring Engine
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-green-700">Do's</h4>
              <ul className="space-y-2">
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Always include complete lead information</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Use consistent question IDs across submissions</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Implement error handling for API calls</span>
                </li>
                <li className="flex items-start space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                  <span className="text-sm">Store and track lead scores over time</span>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-red-700">Don'ts</h4>
              <ul className="space-y-2">
                <li className="flex items-start space-x-2">
                  <div className="w-4 h-4 bg-red-600 rounded-full mt-0.5"></div>
                  <span className="text-sm">Don't submit incomplete or invalid data</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-4 h-4 bg-red-600 rounded-full mt-0.5"></div>
                  <span className="text-sm">Don't ignore API rate limits</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-4 h-4 bg-red-600 rounded-full mt-0.5"></div>
                  <span className="text-sm">Don't hardcode API tokens in client-side code</span>
                </li>
                <li className="flex items-start space-x-2">
                  <div className="w-4 h-4 bg-red-600 rounded-full mt-0.5"></div>
                  <span className="text-sm">Don't rely solely on scores - use human judgment</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Getting Started */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
        <CardHeader>
          <CardTitle>Ready to Get Started?</CardTitle>
          <CardDescription>
            Start integrating the HFC Scoring Engine into your application
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-gray-700">
              Follow these steps to integrate the scoring engine into your application:
            </p>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">1</div>
                <span className="text-sm">Get your API token from the admin panel</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">2</div>
                <span className="text-sm">Choose your preferred integration method</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">3</div>
                <span className="text-sm">Test with sample data using the examples above</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">4</div>
                <span className="text-sm">Implement in your production environment</span>
              </div>
            </div>
            <div className="flex space-x-4">
              <Button asChild>
                <a href="/admin" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Get API Token
                </a>
              </Button>
              <Button variant="outline" asChild>
                <a href="#api-reference">
                  View API Reference
                </a>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ExamplesTab;
