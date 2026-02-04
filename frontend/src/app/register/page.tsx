'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Bot, Eye, EyeOff, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { authApi, usersApi } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

const registerSchema = z.object({
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  username: z.string().min(3, 'Username must be at least 3 characters').regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  email: z.string().email('Please enter a valid email'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ['confirm_password'],
});

type RegisterForm = z.infer<typeof registerSchema>;

const features = [
  'Access to 2 AI agents',
  '50 tasks per month',
  'Email management',
  'Basic scheduling',
  'Dashboard analytics',
];

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await authApi.register({
        full_name: data.full_name,
        username: data.username,
        email: data.email,
        password: data.password,
      });
      const { access_token, refresh_token } = response.data;

      // Get user details
      const userResponse = await usersApi.me();
      const user = userResponse.data;

      setAuth(user, access_token, refresh_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
        <div className="w-full max-w-md space-y-8">
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">AgenticAI</span>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-3xl font-bold text-gray-900">Create your account</h2>
            <p className="mt-2 text-gray-600">Start your free trial - no credit card required</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <Input
              label="Full Name"
              placeholder="John Doe"
              {...register('full_name')}
              error={errors.full_name?.message}
            />

            <Input
              label="Username"
              placeholder="johndoe"
              {...register('username')}
              error={errors.username?.message}
            />

            <Input
              label="Email"
              type="email"
              placeholder="john@example.com"
              {...register('email')}
              error={errors.email?.message}
            />

            <div className="relative">
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Min. 8 characters"
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

            <Input
              label="Confirm Password"
              type="password"
              placeholder="Confirm your password"
              {...register('confirm_password')}
              error={errors.confirm_password?.message}
            />

            <Button type="submit" className="w-full" loading={isLoading}>
              Create account
            </Button>
          </form>

          <p className="text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="text-indigo-600 hover:text-indigo-500 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>

      {/* Right Panel - Features */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-12 flex-col justify-between">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-white/20 backdrop-blur flex items-center justify-center">
              <Bot className="w-7 h-7 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">AgenticAI</span>
          </div>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">Start with Free Tier</h2>
            <p className="text-white/80">Get started with our powerful AI agents at no cost</p>
          </div>

          <div className="bg-white/10 backdrop-blur rounded-xl p-6 space-y-4">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">$0</span>
              <span className="text-white/70">/month</span>
            </div>
            
            <div className="space-y-3">
              {features.map((feature) => (
                <div key={feature} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-white">{feature}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="text-white/70 text-sm">
            <p>Upgrade anytime to Pro ($10/mo) or Premium ($30/mo) for unlimited access</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex -space-x-2">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="w-8 h-8 rounded-full bg-white/20 border-2 border-white/30 flex items-center justify-center text-white text-xs font-medium"
              >
                {['J', 'M', 'A', 'S'][i - 1]}
              </div>
            ))}
          </div>
          <p className="text-white/80 text-sm">Join 10,000+ users already saving time</p>
        </div>
      </div>
    </div>
  );
}
