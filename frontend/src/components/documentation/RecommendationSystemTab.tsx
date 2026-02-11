import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Target, Code, Lightbulb, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const RecommendationSystemTab = () => {
  const ruleExamples = [
    {
      category: 'Question-Based Rules',
      description: 'Trigger recommendations based on specific question answers',
      examples: [
        {
          rule: 'If {credit_score} > 700',
          description: 'High credit score',
          response: 'Premium service recommended'
        },
        {
          rule: 'If {employment_years} < 2',
          description: 'Short employment history',
          response: 'Additional verification required'
        },
        {
          rule: 'If {income} > 50000',
          description: 'High income level',
          response: 'Immediate follow-up required'
        }
      ]
    },
    {
      category: 'Conditional Rules',
      description: 'Trigger recommendations based on specific question conditions',
      examples: [
        {
          rule: 'If {rent_ratio} > 0.3',
          description: 'High rent-to-income ratio',
          response: 'Additional documentation required'
        },
        {
          rule: 'If {credit_score} >= 700',
          description: 'Excellent credit score',
          response: 'Approved - Premium rate available'
        },
        {
          rule: 'If {employment_years} >= 2',
          description: 'Stable employment history',
          response: 'Standard approval process'
        }
      ]
    },
    {
      category: 'Complex Logic Rules',
      description: 'Advanced rules combining multiple conditions',
      examples: [
        {
          rule: 'If {rent_ratio} <= 0.3 and {credit_score} >= 700',
          description: 'Low risk applicant',
          response: 'Fast-track approval available'
        },
        {
          rule: 'If {age} >= 25 and {income} < 30000',
          description: 'Young professional with lower income',
          response: 'Starter package recommended'
        },
        {
          rule: 'If {debt_payments} / {monthly_income} > 0.4',
          description: 'High debt-to-income ratio',
          response: 'Financial counseling suggested'
        }
      ]
    }
  ];

  const availableOperators = [
    {
      type: 'Comparison',
      operators: ['>', '<', '==', '!=', '>=', '<='],
      description: 'Compare values and scores'
    },
    {
      type: 'Logical',
      operators: ['and', 'or', 'not'],
      description: 'Combine multiple conditions'
    },
    {
      type: 'Arithmetic',
      operators: ['+', '-', '*', '/', '%', '**', '//'],
      description: 'Perform calculations in rules'
    }
  ];

  const recommendationTypes = [
    {
      type: 'Approval',
      icon: CheckCircle,
      color: 'green',
      examples: [
        'Approved - Premium rate available',
        'Fast-track approval available',
        'Standard approval process'
      ]
    },
    {
      type: 'Warning',
      icon: AlertTriangle,
      color: 'yellow',
      examples: [
        'Additional documentation required',
        'Financial counseling suggested',
        'Manual review needed'
      ]
    },
    {
      type: 'Rejection',
      icon: XCircle,
      color: 'red',
      examples: [
        'Application declined',
        'Does not meet minimum requirements',
        'Alternative products suggested'
      ]
    }
  ];

  return (
    <div className="space-y-8">
      {/* System Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="mr-2 h-5 w-5" />
            Recommendation System Overview
          </CardTitle>
          <CardDescription>
            Intelligent rule-based system that provides personalized recommendations based on lead responses and calculated scores
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">How It Works</h3>
              <div className="grid md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-bold">1</span>
                  </div>
                  <h4 className="font-semibold text-blue-700 mb-2">Evaluate Rules</h4>
                  <p className="text-sm text-gray-600">
                    System checks each recommendation rule against lead responses and calculated scores
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-purple-600 font-bold">2</span>
                  </div>
                  <h4 className="font-semibold text-purple-700 mb-2">Match Conditions</h4>
                  <p className="text-sm text-gray-600">
                    When rule conditions are met, the corresponding recommendation is triggered
                  </p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-green-600 font-bold">3</span>
                  </div>
                  <h4 className="font-semibold text-green-700 mb-2">Provide Response</h4>
                  <p className="text-sm text-gray-600">
                    Personalized recommendation is delivered with custom messaging and actions
                  </p>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rule Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Code className="mr-2 h-5 w-5" />
            Rule Examples & Patterns
          </CardTitle>
          <CardDescription>
            Comprehensive examples of recommendation rules for different scenarios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {ruleExamples.map((category, categoryIndex) => (
              <div key={categoryIndex} className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{category.category}</h3>
                  <p className="text-sm text-gray-600">{category.description}</p>
                </div>
                <div className="grid gap-4">
                  {category.examples.map((example, exampleIndex) => (
                    <div key={exampleIndex} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="bg-gray-100 p-2 rounded font-mono text-sm mb-2">
                            {example.rule}
                          </div>
                          <p className="text-sm text-gray-700 mb-1">
                            <strong>Condition:</strong> {example.description}
                          </p>
                          <p className="text-sm text-gray-600">
                            <strong>Response:</strong> {example.response}
                          </p>
                        </div>
                        <Badge variant="outline" className="ml-4">
                          {category.category}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Available Operators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="mr-2 h-5 w-5" />
            Available Operators & Functions
          </CardTitle>
          <CardDescription>
            Complete reference of operators and functions you can use in recommendation rules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid md:grid-cols-3 gap-6">
              {availableOperators.map((operatorType, index) => (
                <div key={index} className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">{operatorType.type}</h4>
                  <p className="text-sm text-gray-600 mb-3">{operatorType.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {operatorType.operators.map((op, opIndex) => (
                      <Badge key={opIndex} variant="secondary" className="text-xs">
                        {op}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-gradient-to-r from-green-50 to-blue-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Advanced Functions</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-700 mb-2">Aggregate Functions</h4>
                  <div className="space-y-1 text-sm">
                    <div><code>count({'{field_name}'})</code> - Count occurrences</div>
                    <div><code>max({'{field_name}'})</code> - Maximum value</div>
                    <div><code>mean({'{field_name}'})</code> - Average value</div>
                    <div><code>sum({'{field_name}'})</code> - Sum of values</div>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold text-blue-700 mb-2">Mathematical Functions</h4>
                  <div className="space-y-1 text-sm">
                    <div><code>sqrt({'{field_name}'})</code> - Square root</div>
                    <div><code>days({'{date_field}'})</code> - Days from date</div>
                    <div><code>today()</code> - Current date</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendation Types */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Lightbulb className="mr-2 h-5 w-5" />
            Recommendation Types
          </CardTitle>
          <CardDescription>
            Different types of recommendations you can create for various scenarios
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {recommendationTypes.map((type, index) => {
              const IconComponent = type.icon;
              return (
                <div key={index} className={`bg-${type.color}-50 p-6 rounded-lg`}>
                  <div className="flex items-center mb-4">
                    <IconComponent className={`h-6 w-6 text-${type.color}-600 mr-2`} />
                    <h3 className={`font-semibold text-${type.color}-800`}>{type.type}</h3>
                  </div>
                  <p className={`text-sm text-${type.color}-700 mb-4`}>
                    {type.type === 'Approval' && 'Positive recommendations for qualified leads'}
                    {type.type === 'Warning' && 'Cautionary recommendations requiring attention'}
                    {type.type === 'Rejection' && 'Negative recommendations for unqualified leads'}
                  </p>
                  <div className="space-y-2">
                    <h4 className={`text-sm font-medium text-${type.color}-800`}>Example Messages:</h4>
                    {type.examples.map((example, exampleIndex) => (
                      <div key={exampleIndex} className={`text-xs text-${type.color}-600 bg-white p-2 rounded`}>
                        {example}
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* System Limitations & Workarounds */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <AlertTriangle className="mr-2 h-5 w-5 text-yellow-600" />
            System Limitations & Workarounds
          </CardTitle>
          <CardDescription>
            Important limitations and how to work around them
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-green-800 mb-4">✅ Calculated Scores Now Supported!</h3>
              <p className="text-green-700 mb-4">
                <strong>You can now use calculated scores (X-axis, Y-axis, Total) in recommendation rules!</strong>
              </p>
              <div className="bg-white p-4 rounded border">
                <h4 className="font-semibold text-green-600 mb-2">✅ These now work:</h4>
                <div className="space-y-1 text-sm font-mono text-green-600">
                  <div>If {`{x_axis_score} > 25`}</div>
                  <div>If {`{y_axis_score} < 10`}</div>
                  <div>If {`{total_score} > 50`}</div>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">✅ Available Field Types</h3>
              <p className="text-blue-700 mb-4">
                <strong>You can use both question field names and calculated scores in recommendation rules.</strong>
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded border">
                  <h4 className="font-semibold text-green-600 mb-2">📊 Question Fields:</h4>
                  <div className="space-y-1 text-sm font-mono text-green-600">
                    <div>If {`{credit_score} > 700`}</div>
                    <div>If {`{rent_ratio} <= 0.3`}</div>
                    <div>If {`{employment_years} >= 2`}</div>
                  </div>
                </div>
                <div className="bg-white p-4 rounded border">
                  <h4 className="font-semibold text-blue-600 mb-2">🎯 Calculated Scores:</h4>
                  <div className="space-y-1 text-sm font-mono text-blue-600">
                    <div>If {`{x_axis_score} > 25`}</div>
                    <div>If {`{y_axis_score} < 10`}</div>
                    <div>If {`{total_score} > 50`}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 p-6 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-800 mb-4">🎯 Advanced Score-Based Rules</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-blue-700 mb-2">Direct Score Usage</h4>
                  <p className="text-blue-600 text-sm mb-2">
                    You can now use calculated scores directly in your recommendation rules:
                  </p>
                  <div className="bg-white p-3 rounded border text-sm font-mono">
                    <div className="text-blue-600">If {`{x_axis_score} > 25`}</div>
                    <div className="text-blue-600">If {`{y_axis_score} < 10`}</div>
                    <div className="text-blue-600">If {`{total_score} > 50`}</div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-blue-700 mb-2">Combined Rules</h4>
                  <p className="text-blue-600 text-sm mb-2">
                    Mix calculated scores with question fields for sophisticated logic:
                  </p>
                  <div className="bg-white p-3 rounded border text-sm font-mono">
                    <div className="text-blue-600">If {`{x_axis_score} > 20 and {credit_score} > 700`}</div>
                    <div className="text-blue-600">If {`{total_score} > 40 or {employment_years} >= 5`}</div>
                    <div className="text-blue-600">If {`{y_axis_score} < 15 and {rent_ratio} <= 0.3`}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle>Best Practices</CardTitle>
          <CardDescription>
            Guidelines for creating effective recommendation rules
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h4 className="font-semibold text-green-700">✅ Do's</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    Start rules with "If" for clarity
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    Use specific, measurable conditions
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    Test rules with sample data
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    Create tiered recommendations
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-500 mr-2">•</span>
                    Use meaningful field names
                  </li>
                </ul>
              </div>
              <div className="space-y-4">
                <h4 className="font-semibold text-red-700">❌ Don'ts</h4>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    Create overly complex rules
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    Use undefined field names
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    Forget to test edge cases
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    Create conflicting rules
                  </li>
                  <li className="flex items-start">
                    <span className="text-red-500 mr-2">•</span>
                    Use invalid syntax
                  </li>
                </ul>
              </div>
            </div>

            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-3">Pro Tips</h4>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-700">
                <div>
                  <strong>Score-Based Rules:</strong> Use X/Y axis scores for high-level qualification
                </div>
                <div>
                  <strong>Question Rules:</strong> Use specific questions for detailed conditions
                </div>
                <div>
                  <strong>Combination Rules:</strong> Mix scores and questions for complex logic
                </div>
                <div>
                  <strong>Fallback Rules:</strong> Always have a default recommendation
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-World Example */}
      <Card>
        <CardHeader>
          <CardTitle>Real-World Example: Rental Application</CardTitle>
          <CardDescription>
            Complete example of a rental application recommendation system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-indigo-50 to-purple-50 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Scenario Setup</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-indigo-700 mb-2">Questions</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    <li>• Rent Amount (Slider)</li>
                    <li>• Monthly Income (Integer)</li>
                    <li>• Credit Score (Integer)</li>
                    <li>• Employment Years (Integer)</li>
                    <li>• Debt Payments (Integer)</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold text-purple-700 mb-2">Scoring Model</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    <li>• X-axis: Credit Score + Employment</li>
                    <li>• Y-axis: Income Stability + Debt Ratio</li>
                    <li>• Total Score: X + Y</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Recommendation Rules</h3>
              <div className="grid gap-4">
                <div className="border-l-4 border-green-500 bg-green-50 p-4">
                  <div className="font-mono text-sm mb-2">If {`{rent_ratio} <= 0.3 and {credit_score} >= 700 and {employment_years} >= 2`}</div>
                  <p className="text-sm text-green-700"><strong>Response:</strong> "Approved - Premium rate available. Fast-track processing in 24 hours."</p>
                </div>
                <div className="border-l-4 border-blue-500 bg-blue-50 p-4">
                  <div className="font-mono text-sm mb-2">If {`{rent_ratio} <= 0.4 and {credit_score} >= 650`}</div>
                  <p className="text-sm text-blue-700"><strong>Response:</strong> "Approved - Standard rate. Standard processing time 3-5 business days."</p>
                </div>
                <div className="border-l-4 border-yellow-500 bg-yellow-50 p-4">
                  <div className="font-mono text-sm mb-2">If {`{rent_ratio} > 0.5 or {credit_score} < 600`}</div>
                  <p className="text-sm text-yellow-700"><strong>Response:</strong> "Additional documentation required. Please provide bank statements and employment verification."</p>
                </div>
                <div className="border-l-4 border-red-500 bg-red-50 p-4">
                  <div className="font-mono text-sm mb-2">If {`{debt_payments} / {monthly_income} > 0.4`}</div>
                  <p className="text-sm text-red-700"><strong>Response:</strong> "Application declined. Debt-to-income ratio exceeds maximum threshold."</p>
                </div>
              </div>

              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <h4 className="font-semibold text-green-800 mb-2">✅ Score-Based Rules Now Available</h4>
                <p className="text-green-700 text-sm">
                  The system calculates X-axis and Y-axis scores, and you can now use these calculated scores directly in recommendation rules
                  alongside individual question field names for maximum flexibility.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default RecommendationSystemTab;
