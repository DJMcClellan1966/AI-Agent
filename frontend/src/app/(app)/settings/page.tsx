'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { useAuthStore } from '@/store/authStore';
import {
  User,
  Mail,
  Lock,
  Bell,
  Shield,
  Palette,
  Globe,
  Trash2,
  Save,
  AlertTriangle,
} from 'lucide-react';

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const { user, setAuth, accessToken, refreshToken } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [notifications, setNotifications] = useState({
    emailDigest: true,
    taskAlerts: true,
    agentUpdates: true,
    weeklyReport: false,
    marketingEmails: false,
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: { full_name?: string; email?: string }) => usersApi.update(data),
    onSuccess: (response) => {
      if (accessToken && refreshToken) {
        setAuth(response.data, accessToken, refreshToken);
      }
      queryClient.invalidateQueries({ queryKey: ['user'] });
    },
  });

  const updatePasswordMutation = useMutation({
    mutationFn: (data: { currentPassword: string; newPassword: string }) =>
      usersApi.updatePassword(data.currentPassword, data.newPassword),
    onSuccess: () => {
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    },
  });

  const handleSaveProfile = () => {
    updateProfileMutation.mutate(formData);
  };

  const handleChangePassword = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    updatePasswordMutation.mutate({
      currentPassword: passwordData.currentPassword,
      newPassword: passwordData.newPassword,
    });
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'preferences', label: 'Preferences', icon: Palette },
  ];

  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-500 mt-1">Manage your account settings and preferences.</p>
        </div>

        <div className="flex flex-col md:flex-row gap-8">
          {/* Tabs */}
          <div className="md:w-56 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 space-y-6">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>Update your personal details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center gap-6">
                      <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                        {user?.full_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                      </div>
                      <div>
                        <Button variant="outline" size="sm">
                          Change Avatar
                        </Button>
                        <p className="text-xs text-gray-500 mt-1">JPG, PNG or GIF. Max 2MB.</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="Full Name"
                        value={formData.full_name}
                        onChange={(e) =>
                          setFormData({ ...formData, full_name: e.target.value })
                        }
                      />
                      <Input
                        label="Username"
                        value={user?.username || ''}
                        disabled
                        helperText="Username cannot be changed"
                      />
                      <Input
                        label="Email"
                        type="email"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      />
                    </div>

                    <div className="flex justify-end">
                      <Button
                        onClick={handleSaveProfile}
                        loading={updateProfileMutation.isPending}
                      >
                        <Save className="w-4 h-4 mr-2" />
                        Save Changes
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Subscription</CardTitle>
                    <CardDescription>Your current plan and billing</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-semibold text-gray-900 capitalize">
                            {user?.subscription_tier || 'Free'} Plan
                          </h4>
                          <Badge variant="success">{user?.subscription_status || 'Active'}</Badge>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {user?.subscription_tier === 'free'
                            ? '2 agents, 50 tasks/month'
                            : user?.subscription_tier === 'pro'
                            ? 'All agents, 500 tasks/month'
                            : 'Unlimited access'}
                        </p>
                      </div>
                      <Button variant="outline">Upgrade Plan</Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Change Password</CardTitle>
                    <CardDescription>Update your password regularly for security</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="Current Password"
                      type="password"
                      value={passwordData.currentPassword}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, currentPassword: e.target.value })
                      }
                    />
                    <Input
                      label="New Password"
                      type="password"
                      value={passwordData.newPassword}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, newPassword: e.target.value })
                      }
                    />
                    <Input
                      label="Confirm New Password"
                      type="password"
                      value={passwordData.confirmPassword}
                      onChange={(e) =>
                        setPasswordData({ ...passwordData, confirmPassword: e.target.value })
                      }
                    />
                    <div className="flex justify-end">
                      <Button
                        onClick={handleChangePassword}
                        loading={updatePasswordMutation.isPending}
                        disabled={!passwordData.currentPassword || !passwordData.newPassword}
                      >
                        Update Password
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Two-Factor Authentication</CardTitle>
                    <CardDescription>Add extra security to your account</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Shield className="w-8 h-8 text-gray-400" />
                        <div>
                          <h4 className="font-medium">Two-Factor Authentication</h4>
                          <p className="text-sm text-gray-500">
                            Protect your account with 2FA
                          </p>
                        </div>
                      </div>
                      <Button variant="outline">Enable 2FA</Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Active Sessions</CardTitle>
                    <CardDescription>Manage your active login sessions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                        <div>
                          <h4 className="font-medium">Current Session</h4>
                          <p className="text-sm text-gray-500">
                            Windows • Chrome • Active now
                          </p>
                        </div>
                        <Badge variant="success">Current</Badge>
                      </div>
                    </div>
                    <Button variant="outline" className="mt-4">
                      Log Out All Other Sessions
                    </Button>
                  </CardContent>
                </Card>
              </>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <Card>
                <CardHeader>
                  <CardTitle>Notification Preferences</CardTitle>
                  <CardDescription>Choose what updates you want to receive</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Switch
                    checked={notifications.taskAlerts}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, taskAlerts: checked })
                    }
                    label="Task Alerts"
                    description="Get notified when tasks need approval or are completed"
                  />
                  <Switch
                    checked={notifications.agentUpdates}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, agentUpdates: checked })
                    }
                    label="Agent Updates"
                    description="Notifications about agent status and activity"
                  />
                  <Switch
                    checked={notifications.emailDigest}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, emailDigest: checked })
                    }
                    label="Daily Digest"
                    description="A daily summary of all agent activities"
                  />
                  <Switch
                    checked={notifications.weeklyReport}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, weeklyReport: checked })
                    }
                    label="Weekly Report"
                    description="Weekly summary with insights and statistics"
                  />
                  <Switch
                    checked={notifications.marketingEmails}
                    onCheckedChange={(checked) =>
                      setNotifications({ ...notifications, marketingEmails: checked })
                    }
                    label="Product Updates"
                    description="News about new features and improvements"
                  />
                  <div className="flex justify-end pt-4">
                    <Button>Save Preferences</Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Preferences Tab */}
            {activeTab === 'preferences' && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle>Appearance</CardTitle>
                    <CardDescription>Customize how the app looks</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Palette className="w-5 h-5 text-gray-400" />
                        <div>
                          <h4 className="font-medium">Theme</h4>
                          <p className="text-sm text-gray-500">Choose your preferred theme</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="gap-2">
                          <span className="w-4 h-4 rounded-full bg-white border" />
                          Light
                        </Button>
                        <Button variant="outline" size="sm" className="gap-2">
                          <span className="w-4 h-4 rounded-full bg-gray-900" />
                          Dark
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Language & Region</CardTitle>
                    <CardDescription>Set your locale preferences</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Globe className="w-5 h-5 text-gray-400" />
                        <div>
                          <h4 className="font-medium">Language</h4>
                          <p className="text-sm text-gray-500">English (US)</p>
                        </div>
                      </div>
                      <Button variant="outline" size="sm">
                        Change
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-red-200">
                  <CardHeader>
                    <CardTitle className="text-red-600">Danger Zone</CardTitle>
                    <CardDescription>Irreversible actions</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between p-4 bg-red-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-500" />
                        <div>
                          <h4 className="font-medium text-red-900">Delete Account</h4>
                          <p className="text-sm text-red-600">
                            Permanently delete your account and all data
                          </p>
                        </div>
                      </div>
                      <Button variant="destructive">
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Account
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
