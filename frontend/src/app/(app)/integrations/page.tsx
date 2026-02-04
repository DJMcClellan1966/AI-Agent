'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { integrationsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';
import {
  Mail,
  Calendar,
  CreditCard,
  Cloud,
  Plug,
  Link2,
  Unlink,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Settings,
} from 'lucide-react';

const integrationTypes = [
  {
    value: 'gmail',
    label: 'Gmail',
    icon: Mail,
    description: 'Connect your Gmail account for email management',
    category: 'email',
    color: 'bg-red-500',
  },
  {
    value: 'outlook',
    label: 'Microsoft Outlook',
    icon: Mail,
    description: 'Connect your Outlook account for email management',
    category: 'email',
    color: 'bg-blue-500',
  },
  {
    value: 'google_calendar',
    label: 'Google Calendar',
    icon: Calendar,
    description: 'Sync your Google Calendar for scheduling',
    category: 'calendar',
    color: 'bg-blue-600',
  },
  {
    value: 'outlook_calendar',
    label: 'Outlook Calendar',
    icon: Calendar,
    description: 'Sync your Outlook Calendar for scheduling',
    category: 'calendar',
    color: 'bg-blue-700',
  },
  {
    value: 'stripe',
    label: 'Stripe',
    icon: CreditCard,
    description: 'Connect Stripe for payment processing',
    category: 'payments',
    color: 'bg-purple-600',
  },
  {
    value: 'plaid',
    label: 'Plaid (Banking)',
    icon: CreditCard,
    description: 'Connect your bank accounts for finance tracking',
    category: 'finance',
    color: 'bg-green-600',
  },
  {
    value: 'slack',
    label: 'Slack',
    icon: Cloud,
    description: 'Receive notifications and updates in Slack',
    category: 'notifications',
    color: 'bg-purple-500',
  },
  {
    value: 'zapier',
    label: 'Zapier',
    icon: Plug,
    description: 'Connect to 5000+ apps via Zapier',
    category: 'automation',
    color: 'bg-orange-500',
  },
];

export default function IntegrationsPage() {
  const queryClient = useQueryClient();
  const [selectedIntegration, setSelectedIntegration] = useState<any>(null);
  const [configModalOpen, setConfigModalOpen] = useState(false);

  const { data: integrations, isLoading } = useQuery({
    queryKey: ['integrations'],
    queryFn: () => integrationsApi.list().then((res) => res.data),
  });

  const connectMutation = useMutation({
    mutationFn: (data: { integration_type: string; name: string }) =>
      integrationsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  const disconnectMutation = useMutation({
    mutationFn: (id: number) => integrationsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['integrations'] });
    },
  });

  const getIntegration = (type: string) => {
    return integrations?.find((i: any) => i.provider === type);
  };

  const handleConnect = (type: { value: string; label: string; category: string }) => {
    // In a real app, this would initiate OAuth flow
    connectMutation.mutate({
      integration_type: type.category,
      provider: type.value,
      name: type.label,
    });
  };

  const categories = [
    { id: 'email', label: 'Email', description: 'Connect your email accounts' },
    { id: 'calendar', label: 'Calendar', description: 'Sync your calendars' },
    { id: 'finance', label: 'Finance', description: 'Connect banking and payments' },
    { id: 'notifications', label: 'Notifications', description: 'Get alerts and updates' },
    { id: 'automation', label: 'Automation', description: 'Connect to other services' },
  ];

  return (
    <div className="p-8 space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Integrations</h1>
        <p className="text-gray-500 mt-1">
          Connect your services to enable powerful automations with your AI agents.
        </p>
      </div>

      {/* Connected Integrations Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-xl">
                <CheckCircle className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{integrations?.filter((i: any) => i.is_active).length || 0}</p>
                <p className="text-sm text-gray-500">Active Connections</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-xl">
                <Plug className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{integrationTypes.length}</p>
                <p className="text-sm text-gray-500">Available Services</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-xl">
                <Cloud className="w-6 h-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">Coming Soon</p>
                <p className="text-sm text-gray-500">More integrations</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Integration Categories */}
      {categories.map((category) => {
        const categoryIntegrations = integrationTypes.filter((i) => i.category === category.id);
        if (categoryIntegrations.length === 0) return null;

        return (
          <Card key={category.id}>
            <CardHeader>
              <CardTitle>{category.label}</CardTitle>
              <CardDescription>{category.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {categoryIntegrations.map((integration) => {
                  const connected = getIntegration(integration.value);
                  const IconComponent = integration.icon;

                  return (
                    <div
                      key={integration.value}
                      className={`flex items-center gap-4 p-4 rounded-lg border ${
                        connected ? 'border-green-200 bg-green-50' : 'border-gray-200'
                      }`}
                    >
                      <div className={`p-3 ${integration.color} rounded-xl text-white`}>
                        <IconComponent className="w-6 h-6" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="font-semibold text-gray-900">{integration.label}</h3>
                          {connected && (
                            <Badge variant="success" className="text-xs">
                              Connected
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 truncate">
                          {integration.description}
                        </p>
                      </div>
                      {connected ? (
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedIntegration(connected);
                              setConfigModalOpen(true);
                            }}
                          >
                            <Settings className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              if (confirm('Disconnect this integration?')) {
                                disconnectMutation.mutate(connected.id);
                              }
                            }}
                            loading={disconnectMutation.isPending}
                          >
                            <Unlink className="w-4 h-4 mr-1" />
                            Disconnect
                          </Button>
                        </div>
                      ) : (
                        <Button
                          size="sm"
                          onClick={() => handleConnect(integration)}
                          loading={connectMutation.isPending}
                        >
                          <Link2 className="w-4 h-4 mr-1" />
                          Connect
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        );
      })}

      {/* Coming Soon */}
      <Card>
        <CardHeader>
          <CardTitle>Coming Soon</CardTitle>
          <CardDescription>More integrations we're working on</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {['Discord', 'WhatsApp', 'Notion', 'Trello', 'Asana', 'Linear', 'GitHub', 'Jira'].map(
              (service) => (
                <div
                  key={service}
                  className="p-4 rounded-lg border border-dashed border-gray-200 text-center"
                >
                  <p className="font-medium text-gray-400">{service}</p>
                  <p className="text-xs text-gray-300 mt-1">Coming soon</p>
                </div>
              )
            )}
          </div>
        </CardContent>
      </Card>

      {/* Config Modal */}
      <Modal
        isOpen={configModalOpen}
        onClose={() => {
          setConfigModalOpen(false);
          setSelectedIntegration(null);
        }}
        title={`${selectedIntegration?.name} Settings`}
        size="md"
      >
        {selectedIntegration && (
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span className="text-green-700">Connected and active</span>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Integration Type</h4>
                <p className="mt-1 capitalize">{selectedIntegration.integration_type.replace('_', ' ')}</p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-500">Status</h4>
                <Badge variant={selectedIntegration.is_active ? 'success' : 'secondary'}>
                  {selectedIntegration.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t">
              <Button variant="outline" onClick={() => setConfigModalOpen(false)}>
                Close
              </Button>
              <Button
                variant="destructive"
                onClick={() => {
                  disconnectMutation.mutate(selectedIntegration.id);
                  setConfigModalOpen(false);
                }}
              >
                <Unlink className="w-4 h-4 mr-1" />
                Disconnect
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
