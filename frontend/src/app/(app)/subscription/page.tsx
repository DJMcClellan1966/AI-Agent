'use client';

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { subscriptionsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuthStore } from '@/store/authStore';
import {
  Check,
  Zap,
  Crown,
  Star,
  CreditCard,
  Calendar,
  ArrowRight,
} from 'lucide-react';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    description: 'Perfect for getting started',
    features: [
      '2 AI agents',
      '50 tasks per month',
      'Basic email management',
      'Manual approvals required',
      'Community support',
    ],
    limitations: [
      'No autonomous execution',
      'Limited integrations',
      'Basic analytics',
    ],
    cta: 'Current Plan',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 10,
    description: 'For power users who want more',
    features: [
      'All agent types',
      '500 tasks per month',
      'Basic integrations (Gmail, Calendar)',
      'Some autonomous actions',
      'Email support',
      'Priority task processing',
    ],
    limitations: [],
    cta: 'Upgrade to Pro',
    popular: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    price: 30,
    description: 'For professionals who need everything',
    features: [
      'Unlimited tasks',
      'All integrations',
      'Full autonomous mode',
      'Priority support',
      'Custom agent training',
      'API access',
      'Advanced analytics',
      'White-label options',
    ],
    limitations: [],
    cta: 'Upgrade to Premium',
    popular: false,
  },
];

export default function SubscriptionPage() {
  const { user } = useAuthStore();
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const { data: subscription, isLoading } = useQuery({
    queryKey: ['subscription'],
    queryFn: () => subscriptionsApi.current().then((res) => res.data),
  });

  const upgradeMutation = useMutation({
    mutationFn: (tier: string) => subscriptionsApi.upgrade(tier),
  });

  const currentPlan = user?.subscription_tier || 'free';

  const handleUpgrade = (planId: string) => {
    setSelectedPlan(planId);
    upgradeMutation.mutate(planId);
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Subscription Plans</h1>
          <p className="text-gray-500 mt-2 max-w-2xl mx-auto">
            Choose the plan that best fits your needs. Upgrade anytime to unlock more features and capabilities.
          </p>
        </div>

        {/* Current Plan Summary */}
        <Card className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Crown className="w-5 h-5" />
                  <span className="font-medium">Current Plan</span>
                </div>
                <h2 className="text-2xl font-bold mt-1 capitalize">{currentPlan}</h2>
                <p className="text-white/80 text-sm mt-1">
                  {user?.subscription_status === 'active' ? 'Active subscription' : 'Free tier'}
                </p>
              </div>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-white/80 text-sm">Tasks this month</p>
                  <p className="text-xl font-bold">23 / 50</p>
                </div>
                <div className="text-right">
                  <p className="text-white/80 text-sm">Active agents</p>
                  <p className="text-xl font-bold">2 / 2</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => {
            const isCurrentPlan = currentPlan === plan.id;
            const canUpgrade = plans.findIndex((p) => p.id === currentPlan) < plans.findIndex((p) => p.id === plan.id);

            return (
              <Card
                key={plan.id}
                className={`relative ${
                  plan.popular ? 'border-indigo-500 shadow-lg' : ''
                } ${isCurrentPlan ? 'bg-indigo-50' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <Badge className="bg-indigo-600 text-white px-3">Most Popular</Badge>
                  </div>
                )}
                <CardHeader className="text-center pb-2">
                  <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-indigo-100 flex items-center justify-center">
                    {plan.id === 'free' && <Zap className="w-6 h-6 text-indigo-600" />}
                    {plan.id === 'pro' && <Star className="w-6 h-6 text-indigo-600" />}
                    {plan.id === 'premium' && <Crown className="w-6 h-6 text-indigo-600" />}
                  </div>
                  <CardTitle>{plan.name}</CardTitle>
                  <CardDescription>{plan.description}</CardDescription>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">${plan.price}</span>
                    <span className="text-gray-500">/month</span>
                  </div>
                </CardHeader>
                <CardContent className="pt-6">
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="w-5 h-5 text-green-500 shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-600">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <div className="mt-6">
                    {isCurrentPlan ? (
                      <Button variant="outline" className="w-full" disabled>
                        Current Plan
                      </Button>
                    ) : canUpgrade ? (
                      <Button
                        className="w-full"
                        onClick={() => handleUpgrade(plan.id)}
                        loading={upgradeMutation.isPending && selectedPlan === plan.id}
                      >
                        {plan.cta}
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </Button>
                    ) : (
                      <Button variant="outline" className="w-full" disabled>
                        Downgrade
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* FAQ Section */}
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900">Can I change plans anytime?</h4>
                <p className="text-sm text-gray-500 mt-1">
                  Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">What payment methods do you accept?</h4>
                <p className="text-sm text-gray-500 mt-1">
                  We accept all major credit cards (Visa, MasterCard, Amex) via Stripe.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Is there a free trial for paid plans?</h4>
                <p className="text-sm text-gray-500 mt-1">
                  Yes! Both Pro and Premium plans come with a 14-day free trial.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">What happens when I hit my task limit?</h4>
                <p className="text-sm text-gray-500 mt-1">
                  You'll be notified and can either upgrade or wait until the next month.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Billing Info */}
        <Card>
          <CardHeader>
            <CardTitle>Billing Information</CardTitle>
            <CardDescription>Manage your payment methods and view billing history</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-white rounded-lg shadow-sm">
                  <CreditCard className="w-6 h-6 text-gray-400" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">No payment method on file</p>
                  <p className="text-sm text-gray-500">Add a payment method to upgrade</p>
                </div>
              </div>
              <Button variant="outline">Add Payment Method</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
