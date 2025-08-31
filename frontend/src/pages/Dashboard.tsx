import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { analyticsAPI, LeadAnalytics } from '@/lib/api';
import { 
  Users, 
  BarChart3, 
  Settings, 
  FileText, 
  TrendingUp,
  Target,
  Activity
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<LeadAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await analyticsAPI.getLeadSummary();
        setAnalytics(response.data);
      } catch (err: any) {
        setError('Failed to load analytics');
        console.error('Analytics error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const quickActions = [
    {
      title: 'Questions',
      description: 'Manage scoring questions',
      icon: FileText,
      href: '/questions',
      color: 'bg-blue-500'
    },
    {
      title: 'Scoring Models',
      description: 'Configure scoring formulas',
      icon: BarChart3,
      href: '/scoring-models',
      color: 'bg-green-500'
    },
    {
      title: 'Recommendations',
      description: 'Set up recommendations',
      icon: Target,
      href: '/recommendations',
      color: 'bg-purple-500'
    },
    {
      title: 'Analytics',
      description: 'View detailed reports',
      icon: TrendingUp,
      href: '/analytics',
      color: 'bg-orange-500'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to your scoring engine admin panel</p>
        </div>
        <Button asChild>
          <Link to="/settings">
            <Settings className="mr-2 h-4 w-4" />
            Settings
          </Link>
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Analytics Overview */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Leads</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.total_leads}</div>
              <p className="text-xs text-muted-foreground">
                All time leads processed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg X-Axis Score</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.average_scores.x_axis}</div>
              <p className="text-xs text-muted-foreground">
                Average X-axis score
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Y-Axis Score</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.average_scores.y_axis}</div>
              <p className="text-xs text-muted-foreground">
                Average Y-axis score
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Total Score</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{analytics.average_scores.total}</div>
              <p className="text-xs text-muted-foreground">
                Average total score
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Score Distribution */}
      {analytics && (
        <Card>
          <CardHeader>
            <CardTitle>Score Distribution</CardTitle>
            <CardDescription>
              Distribution of lead scores across different ranges
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">{analytics.score_distribution.low}</div>
                <div className="text-sm text-gray-600">Low Score (0-20)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-600">{analytics.score_distribution.medium}</div>
                <div className="text-sm text-gray-600">Medium Score (20-40)</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{analytics.score_distribution.high}</div>
                <div className="text-sm text-gray-600">High Score (40+)</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Access the most common admin functions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action) => (
              <Link key={action.title} to={action.href}>
                <Card className="hover:shadow-md transition-shadow cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className={`p-2 rounded-lg ${action.color}`}>
                        <action.icon className="h-6 w-6 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold">{action.title}</h3>
                        <p className="text-sm text-gray-600">{action.description}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Latest actions and system updates
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">System Online</p>
                <p className="text-xs text-gray-600">All services are running normally</p>
              </div>
              <Badge variant="secondary">Now</Badge>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm font-medium">API Ready</p>
                <p className="text-xs text-gray-600">All endpoints are available</p>
              </div>
              <Badge variant="secondary">Now</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
