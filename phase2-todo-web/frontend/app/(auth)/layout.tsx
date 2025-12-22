import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Authentication - TodoEvo',
  description: 'Login or create an account to manage your tasks',
}

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 px-4">
      <div className="w-full max-w-md">
        {children}
      </div>
    </div>
  )
}
