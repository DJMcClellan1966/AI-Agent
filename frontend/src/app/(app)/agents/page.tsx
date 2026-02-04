'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Modal } from '@/components/ui/modal';
import {
  Bot,
  Plus,
  Play,
  Pause,
  Trash2,
  Settings,
  Mail,
  Calendar,
  DollarSign,
  ClipboardList,
  Target,
  MoreVertical,
} from 'lucide-react';
import { getAgentTypeIcon, getStatusColor } from '@/lib/utils';

const agentTypes = [
  { value: 'email', label: 'Email Agent', icon: Mail, description: 'Manages your emails, drafts responses, and schedules follow-ups' },
  { value: 'scheduler', label: 'Scheduler Agent', icon: Calendar, description: 'Books appointments, finds optimal meeting times, and manages your calendar' },
  { value: 'finance', label: 'Finance Agent', icon: DollarSign, description: 'Tracks bills, negotiates with providers, and finds better rates' },
  { value: 'planning', label: 'Planning Agent', icon: ClipboardList, description: 'Optimizes daily routines and suggests task prioritization' },
  { value: 'coordinator', label: 'Coordinator Agent', icon: Target, description: 'Orchestrates other agents and manages inter-agent communication' },
];

export default function AgentsPage() {
  const queryClient = useQueryClient();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [formData, setFormData] = useState({
    agent_type: '',
    name: '',
    description: '',
    can_execute_autonomously: false,
    requires_approval: true,
    max_daily_tasks: 50,
  });

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.list().then((res) => res.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: typeof formData) => agentsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      setIsCreateModalOpen(false);
      resetForm();
    },
  });

  const activateMutation = useMutation({
    mutationFn: (id: number) => agentsApi.activate(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agents'] }),
  });

  const pauseMutation = useMutation({
    mutationFn: (id: number) => agentsApi.pause(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agents'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => agentsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['agents'] }),
  });

  const resetForm = () => {
    setFormData({
      agent_type: '',
      name: '',
      description: '',
      can_execute_autonomously: false,
      requires_approval: true,
      max_daily_tasks: 50,
    });
  };

  const handleCreate = () => {
    createMutation.mutate(formData);
  };

  const getAgentIcon = (type: string) => {
    const agent = agentTypes.find((a) => a.value === type);
    if (agent) {
      const IconComponent = agent.icon;
      return <IconComponent className="w-6 h-6" />;
    }
    return <Bot className="w-6 h-6" />;
  };

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Agents</h1>
          <p className="text-gray-500 mt-1">
            Manage your autonomous AI agents that work for you 24/7.
          </p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Agent
        </Button>
      </div>

      {/* Agent Type Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agentTypes.map((type) => {
          const agentCount = agents?.filter((a: any) => a.agent_type === type.value).length || 0;
          const IconComponent = type.icon;
          
          return (
            <Card
              key={type.value}
              className="cursor-pointer hover:border-indigo-300 transition-colors"
              onClick={() => {
                setFormData({ ...formData, agent_type: type.value, name: type.label });
                setIsCreateModalOpen(true);
              }}
            >
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl text-white">
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{type.label}</h3>
                    <p className="text-sm text-gray-500 mt-1">{type.description}</p>
                    <p className="text-xs text-indigo-600 mt-2">
                      {agentCount > 0 ? `${agentCount} active` : 'Click to create'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Active Agents List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Agents</CardTitle>
          <CardDescription>All your configured AI agents</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse flex items-center gap-4 p-4 border rounded-lg">
                  <div className="w-12 h-12 bg-gray-200 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-1/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : agents && agents.length > 0 ? (
            <div className="space-y-4">
              {agents.map((agent: any) => (
                <div
                  key={agent.id}
                  className="flex items-center gap-4 p-4 border rounded-lg hover:border-gray-300 transition-colors"
                >
                  <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl text-white">
                    {getAgentIcon(agent.agent_type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                      <Badge className={getStatusColor(agent.status)}>
                        {agent.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-500 mt-1 truncate">
                      {agent.description || `${agent.agent_type} agent`}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span>
                        {agent.can_execute_autonomously ? 'Autonomous' : 'Manual approval'}
                      </span>
                      <span>Max {agent.max_daily_tasks} tasks/day</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {agent.status === 'active' ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => pauseMutation.mutate(agent.id)}
                        disabled={pauseMutation.isPending}
                      >
                        <Pause className="w-4 h-4 mr-1" />
                        Pause
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => activateMutation.mutate(agent.id)}
                        disabled={activateMutation.isPending}
                      >
                        <Play className="w-4 h-4 mr-1" />
                        Activate
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setSelectedAgent(agent)}
                    >
                      <Settings className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this agent?')) {
                          deleteMutation.mutate(agent.id);
                        }
                      }}
                      disabled={deleteMutation.isPending}
                    >
                      <Trash2 className="w-4 h-4 text-red-500" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Bot className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-gray-900 font-medium">No agents yet</h3>
              <p className="text-gray-500 text-sm mt-1 mb-4">
                Create your first AI agent to automate your tasks.
              </p>
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Create Agent
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Agent Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetForm();
        }}
        title="Create New Agent"
        description="Configure your AI agent's capabilities and permissions."
        size="lg"
      >
        <div className="space-y-6">
          <Select
            label="Agent Type"
            value={formData.agent_type}
            onChange={(e) => {
              const type = agentTypes.find((t) => t.value === e.target.value);
              setFormData({
                ...formData,
                agent_type: e.target.value,
                name: type?.label || '',
              });
            }}
            options={agentTypes.map((t) => ({ value: t.value, label: t.label }))}
            placeholder="Select agent type"
          />

          <Input
            label="Agent Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="My Email Agent"
          />

          <Textarea
            label="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Describe what this agent should do..."
          />

          <div className="space-y-4 pt-4 border-t">
            <h4 className="font-medium text-gray-900">Permissions</h4>
            
            <Switch
              checked={formData.can_execute_autonomously}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, can_execute_autonomously: checked })
              }
              label="Autonomous Execution"
              description="Allow agent to act without manual approval"
            />

            <Switch
              checked={formData.requires_approval}
              onCheckedChange={(checked) =>
                setFormData({ ...formData, requires_approval: checked })
              }
              label="Require Approval for Important Actions"
              description="Agent will ask before taking major actions"
            />

            <Input
              type="number"
              label="Max Daily Tasks"
              value={formData.max_daily_tasks}
              onChange={(e) =>
                setFormData({ ...formData, max_daily_tasks: parseInt(e.target.value) || 50 })
              }
              min={1}
              max={500}
            />
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateModalOpen(false);
                resetForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreate}
              loading={createMutation.isPending}
              disabled={!formData.agent_type || !formData.name}
            >
              Create Agent
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
