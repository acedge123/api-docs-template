import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart3, Target, TrendingUp, Calculator } from 'lucide-react';

const ScoringAlgorithmTab = () => {
  const scoringFactors = [
    {
      factor: 'Job Title',
      weight: 'High',
      description: 'C-level executives score higher than junior positions',
      examples: ['CEO (100)', 'CTO (95)', 'Manager (70)', 'Analyst (40)']
    },
    {
      factor: 'Company Size',
      weight: 'Medium',
      description: 'Larger companies typically have bigger budgets',
      examples: ['1000+ employees (90)', '500-999 (80)', '100-499 (70)', '<100 (50)']
    },
    {
      factor: 'Budget Range',
      weight: 'High',
      description: 'Higher budgets indicate more serious prospects',
      examples: ['$500k+ (100)', '$100k-500k (85)', '$50k-100k (70)', '<$50k (40)']
    },
    {
      factor: 'Timeline',
      weight: 'Medium',
      description: 'Shorter timelines suggest urgency and higher intent',
      examples: ['Immediate (90)', '1-3 months (80)', '3-6 months (60)', '6+ months (40)']
    }
  ];

  const xAxisFactors = [
    'Job Title Weight',
    'Company Size Weight', 
    'Industry Relevance',
    'Decision Making Authority'
  ];

  const yAxisFactors = [
    'Budget Range Weight',
    'Timeline Urgency',
    'Project Scope',
    'Technical Sophistication'
  ];

  return (
    <div className="space-y-8">
      {/* Algorithm Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <BarChart3 className="mr-2 h-5 w-5" />
            Scoring Algorithm Overview
          </CardTitle>
          <CardDescription>
            How our X/Y axis scoring system evaluates and qualifies leads
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Two-Dimensional Scoring</h3>
              <p className="text-gray-700 mb-4">
                Our algorithm uses a sophisticated X/Y axis scoring system that evaluates leads across two key dimensions:
              </p>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-blue-700 mb-2">X-Axis: Lead Quality</h4>
                  <p className="text-sm text-gray-600">
                    Measures the prospect's authority, company size, and decision-making power
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold text-purple-700 mb-2">Y-Axis: Purchase Intent</h4>
                  <p className="text-sm text-gray-600">
                    Evaluates budget, timeline, project scope, and technical sophistication
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Scoring Factors */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="mr-2 h-5 w-5" />
            Key Scoring Factors
          </CardTitle>
          <CardDescription>
            The primary factors that influence lead scoring and their relative weights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {scoringFactors.map((factor, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">{factor.factor}</h4>
                  <Badge 
                    variant={factor.weight === 'High' ? 'default' : 'secondary'}
                    className="text-xs"
                  >
                    {factor.weight} Weight
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">{factor.description}</p>
                <div>
                  <span className="text-xs text-gray-500 font-medium">Example Scores:</span>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {factor.examples.map((example, i) => (
                      <Badge key={i} variant="outline" className="text-xs">
                        {example}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* X/Y Axis Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Calculator className="mr-2 h-5 w-5" />
            X/Y Axis Calculation
          </CardTitle>
          <CardDescription>
            Detailed breakdown of how X and Y axis scores are calculated
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-semibold text-blue-700">X-Axis Factors (Lead Quality)</h4>
              <div className="space-y-2">
                {xAxisFactors.map((factor, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-sm">{factor}</span>
                  </div>
                ))}
              </div>
              <div className="bg-blue-50 p-3 rounded">
                <p className="text-xs text-blue-800">
                  <strong>Formula:</strong> (Job Title × 0.4) + (Company Size × 0.3) + (Industry × 0.2) + (Authority × 0.1)
                </p>
              </div>
            </div>
            <div className="space-y-4">
              <h4 className="font-semibold text-purple-700">Y-Axis Factors (Purchase Intent)</h4>
              <div className="space-y-2">
                {yAxisFactors.map((factor, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <span className="text-sm">{factor}</span>
                  </div>
                ))}
              </div>
              <div className="bg-purple-50 p-3 rounded">
                <p className="text-xs text-purple-800">
                  <strong>Formula:</strong> (Budget × 0.4) + (Timeline × 0.3) + (Scope × 0.2) + (Tech × 0.1)
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Qualification Categories */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Qualification Categories
          </CardTitle>
          <CardDescription>
            How X/Y scores translate into actionable qualification categories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-green-600 font-bold">A</span>
              </div>
              <h4 className="font-semibold text-green-800">High Priority</h4>
              <p className="text-xs text-green-700 mt-1">X: 80-100, Y: 80-100</p>
              <p className="text-xs text-green-600 mt-2">Contact immediately</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-blue-600 font-bold">B</span>
              </div>
              <h4 className="font-semibold text-blue-800">Medium Priority</h4>
              <p className="text-xs text-blue-700 mt-1">X: 60-79, Y: 60-79</p>
              <p className="text-xs text-blue-600 mt-2">Follow up within week</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-yellow-600 font-bold">C</span>
              </div>
              <h4 className="font-semibold text-yellow-800">Low Priority</h4>
              <p className="text-xs text-yellow-700 mt-1">X: 40-59, Y: 40-59</p>
              <p className="text-xs text-yellow-600 mt-2">Nurture campaign</p>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-red-600 font-bold">D</span>
              </div>
              <h4 className="font-semibold text-red-800">Disqualified</h4>
              <p className="text-xs text-red-700 mt-1">X: 0-39, Y: 0-39</p>
              <p className="text-xs text-red-600 mt-2">Archive or reject</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Customization */}
      <Card>
        <CardHeader>
          <CardTitle>Algorithm Customization</CardTitle>
          <CardDescription>
            How to customize the scoring algorithm for your specific needs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Custom Weights</h4>
              <p className="text-sm text-gray-600">
                Adjust the relative importance of different factors based on your industry and target market.
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Custom Questions</h4>
              <p className="text-sm text-gray-600">
                Add industry-specific questions to gather more relevant qualification data.
              </p>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold mb-2">Threshold Adjustments</h4>
              <p className="text-sm text-gray-600">
                Modify qualification thresholds to match your sales process and capacity.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ScoringAlgorithmTab;
