'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Bot, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { authApi, usersApi } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

const loginSchema = z.object({
  username: z.string().min(1, 'Username or email is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await authApi.login(data.username, data.password);
      const { access_token, refresh_token } = response.data;

      // Get user details
      const userResponse = await usersApi.me();
      const user = userResponse.data;

      setAuth(user, access_token, refresh_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">AgenticAI</span>
          </div>
        </div>
        
        <div className="space-y-6">
          <h1 className="text-4xl font-bold text-white leading-tight">
            Your AI-Powered<br />Life Assistant
          </h1>
          <p className="text-lg text-white/80 max-w-md">
            Autonomous agents that handle your daily tasks - from managing emails to 
            booking appointments and negotiating bills.
          </p>
          
          <div className="grid grid-cols-2 gap-4 pt-4">
            {[
              { icon: '📧', title: 'Email Management', desc: 'Smart sorting & responses' },
              { icon: '📅', title: 'Scheduling', desc: 'Automated booking' },
              { icon: '💰', title: 'Bill Negotiation', desc: 'Save money automatically' },
              { icon: '📋', title: 'Planning', desc: 'Optimized routines' },
            ].map((feature) => (
              <div key={feature.title} className="bg-white/10 backdrop-blur rounded-lg p-4">
                <span className="text-2xl">{feature.icon}</span>
                <h3 className="font-semibold text-white mt-2">{feature.title}</h3>
                <p className="text-sm text-white/70">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <p className="text-white/60 text-sm">
          Trusted by thousands of users worldwide
        </p>
      </div>

      {/* Right Panel - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AgenticAI</span>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold text-gray-900">Welcome back</h2>
            <p className="mt-2 text-gray-600">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Input
              label="Username or Email"
              placeholder="Enter your username or email"
              {...register('username')}
              error={errors.username?.message}
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Enter your password"
                {...register('password')}
                error={errors.password?.message}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-9 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                <span className="text-sm text-gray-600">Remember me</span>
              </label>
              <Link href="/forgot-password" className="text-sm text-indigo-600 hover:text-indigo-500">
                Forgot password?
              </Link>
            </div>

            <Button type="submit" className="w-full" loading={isLoading}>
              Sign in
            </Button>
          </form>

          <p className="text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link href="/register" className="text-indigo-600 hover:text-indigo-500 font-medium">
              Sign up for free
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
