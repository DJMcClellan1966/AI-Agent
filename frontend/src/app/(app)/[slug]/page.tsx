'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { notFound } from 'next/navigation';

const REDIRECT_TO_IDE = ['dashboard', 'agents', 'tasks', 'integrations', 'subscription'];

export default function RedirectPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params?.slug as string;

  useEffect(() => {
    if (REDIRECT_TO_IDE.includes(slug)) router.replace('/ide');
  }, [slug, router]);

  if (!REDIRECT_TO_IDE.includes(slug)) notFound();
  return <div className="flex items-center justify-center h-full text-[#8888a0]">Redirecting…</div>;
}
