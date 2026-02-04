'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

const publicPaths = ['/login', '/register', '/forgot-password'];

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, accessToken } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const isPublicPath = publicPaths.some((path) => pathname.startsWith(path));

    if (!isAuthenticated && !isPublicPath) {
      router.replace('/login');
    } else if (isAuthenticated && isPublicPath) {
      router.replace('/dashboard');
    } else {
      setIsLoading(false);
    }
  }, [isAuthenticated, pathname, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
          <p className="text-gray-500">Loading...</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
