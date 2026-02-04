'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi, agentsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select } from '@/components/ui/select';
import { Modal } from '@/components/ui/modal';
import {
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  Filter,
  RefreshCw,
  Eye,
  Check,
  X,
  Bot,
} from 'lucide-react';
import { formatDateTime, getStatusColor, getPriorityColor, getAgentTypeIcon } from '@/lib/utils';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: 'awaiting_approval', label: 'Awaiting Approval' },
  { value: 'approved', label: 'Approved' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const priorityOptions = [
  { value: '', label: 'All Priorities' },
  { value: 'urgent', label: 'Urgent' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
];

export default function TasksPage() {
  const queryClient = useQueryClient();
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [selectedTask, setSelectedTask] = useState<any>(null);

  const { data: tasks, isLoading, refetch } = useQuery({
    queryKey: ['tasks', statusFilter, priorityFilter],
    queryFn: () =>
      tasksApi
        .list({
          status: statusFilter || undefined,
          priority: priorityFilter || undefined,
          limit: 50,
        })
        .then((res) => res.data),
  });

  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.list().then((res) => res.data),
  });

  const approveMutation = useMutation({
    mutationFn: (id: number) => tasksApi.approve(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setSelectedTask(null);
    },
  });

  const rejectMutation = useMutation({
    mutationFn: (id: number) => tasksApi.reject(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setSelectedTask(null);
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: number) => tasksApi.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setSelectedTask(null);
    },
  });

  const getAgentName = (agentId: number) => {
    const agent = agents?.find((a: any) => a.id === agentId);
    return agent?.name || 'Unknown Agent';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'awaiting_approval':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'in_progress':
        return <RefreshCw className="w-5 h-5 text-purple-500 animate-spin" />;
      case 'cancelled':
        return <X className="w-5 h-5 text-gray-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const pendingApproval = tasks?.filter((t: any) => t.status === 'awaiting_approval') || [];
  const otherTasks = tasks?.filter((t: any) => t.status !== 'awaiting_approval') || [];

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="text-gray-500 mt-1">Review and manage tasks from your AI agents.</p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>
            <Select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              options={statusOptions}
              className="w-48"
            />
            <Select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              options={priorityOptions}
              className="w-40"
            />
            {(statusFilter || priorityFilter) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setStatusFilter('');
                  setPriorityFilter('');
                }}
              >
                Clear filters
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Pending Approval Section */}
      {pendingApproval.length > 0 && (
        <Card className="border-blue-200 bg-blue-50/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-600" />
              <CardTitle className="text-blue-900">Awaiting Your Approval</CardTitle>
            </div>
            <CardDescription>
              {pendingApproval.length} task{pendingApproval.length > 1 ? 's' : ''} need your
              review
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {pendingApproval.map((task: any) => (
                <div
                  key={task.id}
                  className="flex items-center gap-4 p-4 bg-white rounded-lg border border-blue-100"
                >
                  <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center text-xl">
                    {getAgentTypeIcon(task.task_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900">{task.title}</h4>
                    <p className="text-sm text-gray-500 truncate">{task.description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      From {getAgentName(task.agent_id)} • {formatDateTime(task.created_at)}
                    </p>
                  </div>
                  <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                  <div className="flex items-center gap-2">
                    <Button
                      size="sm"
                      onClick={() => approveMutation.mutate(task.id)}
                      loading={approveMutation.isPending}
                    >
                      <Check className="w-4 h-4 mr-1" />
                      Approve
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => rejectMutation.mutate(task.id)}
                      loading={rejectMutation.isPending}
                    >
                      <X className="w-4 h-4 mr-1" />
                      Reject
                    </Button>
                    <Button variant="ghost" size="icon" onClick={() => setSelectedTask(task)}>
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* All Tasks */}
      <Card>
        <CardHeader>
          <CardTitle>All Tasks</CardTitle>
          <CardDescription>
            {tasks?.length || 0} total tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="animate-pulse flex items-center gap-4 p-4 border rounded-lg">
                  <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/3" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : tasks && tasks.length > 0 ? (
            <div className="space-y-3">
              {tasks.map((task: any) => (
                <div
                  key={task.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:border-gray-300 transition-colors cursor-pointer"
                  onClick={() => setSelectedTask(task)}
                >
                  {getStatusIcon(task.status)}
                  <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center text-xl">
                    {getAgentTypeIcon(task.task_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900">{task.title}</h4>
                    <p className="text-sm text-gray-500 truncate">{task.description}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {getAgentName(task.agent_id)} • {formatDateTime(task.created_at)}
                    </p>
                  </div>
                  <Badge className={getPriorityColor(task.priority)}>{task.priority}</Badge>
                  <Badge className={getStatusColor(task.status)}>
                    {task.status.replace('_', ' ')}
                  </Badge>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Bot className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-gray-900 font-medium">No tasks found</h3>
              <p className="text-gray-500 text-sm mt-1">
                {statusFilter || priorityFilter
                  ? 'Try adjusting your filters.'
                  : 'Your agents will create tasks as they work.'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Task Detail Modal */}
      <Modal
        isOpen={!!selectedTask}
        onClose={() => setSelectedTask(null)}
        title={selectedTask?.title}
        size="lg"
      >
        {selectedTask && (
          <div className="space-y-6">
            <div className="flex items-center gap-4">
              {getStatusIcon(selectedTask.status)}
              <Badge className={getStatusColor(selectedTask.status)}>
                {selectedTask.status.replace('_', ' ')}
              </Badge>
              <Badge className={getPriorityColor(selectedTask.priority)}>
                {selectedTask.priority} priority
              </Badge>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Description</h4>
                <p className="mt-1 text-gray-900">{selectedTask.description || 'No description'}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Agent</h4>
                  <p className="mt-1 text-gray-900">{getAgentName(selectedTask.agent_id)}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Task Type</h4>
                  <p className="mt-1 text-gray-900 capitalize">{selectedTask.task_type}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Created</h4>
                  <p className="mt-1 text-gray-900">{formatDateTime(selectedTask.created_at)}</p>
                </div>
                {selectedTask.completed_at && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-500">Completed</h4>
                    <p className="mt-1 text-gray-900">
                      {formatDateTime(selectedTask.completed_at)}
                    </p>
                  </div>
                )}
              </div>

              {selectedTask.result && (
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Result</h4>
                  <pre className="mt-1 p-3 bg-gray-50 rounded-lg text-sm overflow-auto">
                    {JSON.stringify(selectedTask.result, null, 2)}
                  </pre>
                </div>
              )}

              {selectedTask.error && (
                <div>
                  <h4 className="text-sm font-medium text-red-500">Error</h4>
                  <p className="mt-1 text-red-600 bg-red-50 p-3 rounded-lg">
                    {selectedTask.error}
                  </p>
                </div>
              )}
            </div>

            {selectedTask.status === 'awaiting_approval' && (
              <div className="flex justify-end gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => rejectMutation.mutate(selectedTask.id)}
                  loading={rejectMutation.isPending}
                >
                  <X className="w-4 h-4 mr-1" />
                  Reject
                </Button>
                <Button
                  onClick={() => approveMutation.mutate(selectedTask.id)}
                  loading={approveMutation.isPending}
                >
                  <Check className="w-4 h-4 mr-1" />
                  Approve
                </Button>
              </div>
            )}

            {['approved', 'in_progress'].includes(selectedTask.status) && (
              <div className="flex justify-end pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => cancelMutation.mutate(selectedTask.id)}
                  loading={cancelMutation.isPending}
                >
                  Cancel Task
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
