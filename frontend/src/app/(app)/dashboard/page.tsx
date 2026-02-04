'use client';

import { useQuery } from '@tanstack/react-query';
import { agentsApi, tasksApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Activity,
  Bot,
  CheckCircle,
  Clock,
  AlertCircle,
  TrendingUp,
  Zap,
  Calendar,
  ArrowRight,
  Plus,
} from 'lucide-react';
import Link from 'next/link';
import { formatRelativeTime, getStatusColor, getAgentTypeIcon } from '@/lib/utils';
import { useAuthStore } from '@/store/authStore';

export default function DashboardPage() {
  const { user } = useAuthStore();
  
  const { data: agents, isLoading: agentsLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.list().then((res) => res.data),
  });

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.list({ limit: 10 }).then((res) => res.data),
  });

  const activeAgents = agents?.filter((a: any) => a.status === 'active').length || 0;
  const totalAgents = agents?.length || 0;
  const pendingTasks = tasks?.filter((t: any) => t.status === 'awaiting_approval').length || 0;
  const completedTasks = tasks?.filter((t: any) => t.status === 'completed').length || 0;
  const inProgressTasks = tasks?.filter((t: any) => t.status === 'in_progress').length || 0;
  const failedTasks = tasks?.filter((t: any) => t.status === 'failed').length || 0;

  const recentTasks = tasks?.slice(0, 5) || [];

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name?.split(' ')[0] || user?.username || 'there'}!
          </h1>
          <p className="text-gray-500 mt-1">
            Here's what's happening with your AI agents today.
          </p>
        </div>
        <Link href="/agents">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Agent
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Active Agents</CardTitle>
            <div className="p-2 bg-indigo-100 rounded-lg">
              <Bot className="h-4 w-4 text-indigo-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{activeAgents}</div>
            <p className="text-sm text-gray-500 mt-1">
              {totalAgents > 0 ? `of ${totalAgents} total` : 'No agents yet'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Pending Approval</CardTitle>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Clock className="h-4 w-4 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{pendingTasks}</div>
            <p className="text-sm text-gray-500 mt-1">Tasks waiting for you</p>
            {pendingTasks > 0 && (
              <Link href="/tasks?status=awaiting_approval" className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1 mt-2">
                Review now <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Completed Today</CardTitle>
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="h-4 w-4 text-green-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{completedTasks}</div>
            <p className="text-sm text-gray-500 mt-1">Tasks done</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">In Progress</CardTitle>
            <div className="p-2 bg-purple-100 rounded-lg">
              <Activity className="h-4 w-4 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">{inProgressTasks}</div>
            <p className="text-sm text-gray-500 mt-1">Being processed</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Tasks */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Tasks</CardTitle>
              <CardDescription>Latest activity from your agents</CardDescription>
            </div>
            <Link href="/tasks">
              <Button variant="outline" size="sm">View all</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {tasksLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse flex items-center gap-4">
                    <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-1/2" />
                      <div className="h-3 bg-gray-200 rounded w-3/4" />
                    </div>
                  </div>
                ))}
              </div>
            ) : recentTasks.length > 0 ? (
              <div className="space-y-4">
                {recentTasks.map((task: any) => (
                  <div
                    key={task.id}
                    className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-xl">
                      {getAgentTypeIcon(task.task_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-medium text-gray-900 truncate">{task.title}</h4>
                      <p className="text-sm text-gray-500 truncate">{task.description}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs text-gray-400">
                        {formatRelativeTime(task.created_at)}
                      </span>
                      <Badge className={getStatusColor(task.status)}>
                        {task.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <Calendar className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-gray-900 font-medium">No tasks yet</h3>
                <p className="text-gray-500 text-sm mt-1">
                  Your agents will create tasks as they work for you.
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Agent Overview */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Your Agents</CardTitle>
              <CardDescription>Quick overview</CardDescription>
            </div>
            <Link href="/agents">
              <Button variant="outline" size="sm">Manage</Button>
            </Link>
          </CardHeader>
          <CardContent>
            {agentsLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse flex items-center gap-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                    <div className="flex-1">
                      <div className="h-4 bg-gray-200 rounded w-24 mb-2" />
                      <div className="h-3 bg-gray-200 rounded w-16" />
                    </div>
                  </div>
                ))}
              </div>
            ) : agents && agents.length > 0 ? (
              <div className="space-y-4">
                {agents.slice(0, 5).map((agent: any) => (
                  <div key={agent.id} className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-lg">
                      {getAgentTypeIcon(agent.agent_type)}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{agent.name}</h4>
                      <p className="text-sm text-gray-500 capitalize">{agent.agent_type}</p>
                    </div>
                    <Badge
                      variant={agent.status === 'active' ? 'success' : 'secondary'}
                    >
                      {agent.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-12 h-12 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-3">
                  <Bot className="w-6 h-6 text-gray-400" />
                </div>
                <h3 className="text-gray-900 font-medium">No agents yet</h3>
                <p className="text-gray-500 text-sm mt-1 mb-4">
                  Create your first AI agent to get started.
                </p>
                <Link href="/agents">
                  <Button size="sm">
                    <Plus className="w-4 h-4 mr-1" />
                    Create Agent
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks you might want to do</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/agents" className="group">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50 transition-colors">
                <div className="p-3 bg-indigo-100 rounded-lg group-hover:bg-indigo-200 transition-colors">
                  <Bot className="w-6 h-6 text-indigo-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Create Agent</h4>
                  <p className="text-sm text-gray-500">Set up a new AI agent</p>
                </div>
              </div>
            </Link>
            
            <Link href="/tasks?status=awaiting_approval" className="group">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors">
                <div className="p-3 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                  <Clock className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Review Tasks</h4>
                  <p className="text-sm text-gray-500">Approve pending actions</p>
                </div>
              </div>
            </Link>
            
            <Link href="/integrations" className="group">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors">
                <div className="p-3 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                  <Zap className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">Connect Services</h4>
                  <p className="text-sm text-gray-500">Link email, calendar</p>
                </div>
              </div>
            </Link>
            
            <Link href="/settings" className="group">
              <div className="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
                <div className="p-3 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">View Analytics</h4>
                  <p className="text-sm text-gray-500">Track performance</p>
                </div>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
