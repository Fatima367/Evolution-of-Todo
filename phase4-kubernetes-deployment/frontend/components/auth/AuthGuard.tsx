'use client'

import React, { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/auth'
import { Loading } from '@/components/ui/Loading'

export interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
  redirectTo?: string
  fallback?: React.ReactNode
}

/**
 * AuthGuard component to protect routes and handle authentication
 *
 * @param requireAuth - If true, requires user to be authenticated (default: true)
 * @param redirectTo - Path to redirect to if auth check fails (default: /auth/login for requireAuth, / for guest-only)
 * @param fallback - Optional custom fallback component while checking auth status
 */
export const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requireAuth = true,
  redirectTo,
  fallback,
}) => {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (isLoading) return

    if (requireAuth && !isAuthenticated) {
      // User needs to be authenticated but isn't
      const redirect = redirectTo || `/auth/login?redirect=${encodeURIComponent(pathname)}`
      router.push(redirect)
    } else if (!requireAuth && isAuthenticated) {
      // Guest-only route but user is authenticated
      const redirect = redirectTo || '/tasks'
      router.push(redirect)
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, pathname, router])

  // Show loading state while checking authentication
  if (isLoading) {
    if (fallback) {
      return <>{fallback}</>
    }
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Loading..." />
      </div>
    )
  }

  // Show children only if auth requirements are met
  if (requireAuth && !isAuthenticated) {
    // Will redirect, show loading
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Redirecting..." />
      </div>
    )
  }

  if (!requireAuth && isAuthenticated) {
    // Will redirect, show loading
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Redirecting..." />
      </div>
    )
  }

  return <>{children}</>
}

/**
 * Higher-order component to wrap a component with AuthGuard
 *
 * @example
 * const ProtectedPage = withAuthGuard(MyPage)
 * const GuestOnlyPage = withAuthGuard(MyLoginPage, { requireAuth: false })
 */
export function withAuthGuard<P extends object>(
  Component: React.ComponentType<P>,
  options?: Omit<AuthGuardProps, 'children'>
) {
  return function WithAuthGuardComponent(props: P) {
    return (
      <AuthGuard {...options}>
        <Component {...props} />
      </AuthGuard>
    )
  }
}

/**
 * Hook to check if user has permission (can be extended for role-based access)
 */
export function useRequireAuth() {
  const { isAuthenticated, isLoading, user } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push(`/auth/login?redirect=${encodeURIComponent(pathname)}`)
    }
  }, [isAuthenticated, isLoading, pathname, router])

  return {
    isAuthenticated,
    isLoading,
    user,
  }
}

/**
 * Render prop component for conditional rendering based on auth status
 *
 * @example
 * <AuthCheck
 *   authenticated={<Dashboard />}
 *   unauthenticated={<LandingPage />}
 *   loading={<LoadingSpinner />}
 * />
 */
export interface AuthCheckProps {
  authenticated: React.ReactNode
  unauthenticated: React.ReactNode
  loading?: React.ReactNode
}

export const AuthCheck: React.FC<AuthCheckProps> = ({
  authenticated,
  unauthenticated,
  loading,
}) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <>{loading || <Loading size="lg" />}</>
  }

  return <>{isAuthenticated ? authenticated : unauthenticated}</>
}
