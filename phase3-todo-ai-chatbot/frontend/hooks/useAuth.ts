'use client';

import { useAuth as useAuthContext } from '@/contexts/auth';

// Re-export the useAuth hook from contexts/auth for consistency with plan.md
export function useAuth() {
  return useAuthContext();
}
