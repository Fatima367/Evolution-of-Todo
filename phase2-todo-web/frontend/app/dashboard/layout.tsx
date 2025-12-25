'use client'

import { DashboardSidebar } from '@/components/layout/DashboardSidebar'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { EditTaskModal } from '@/components/tasks/EditTaskModal'
import { DeleteConfirmModal } from '@/components/tasks/DeleteConfirmModal'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading || !isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F7F6F7] via-white to-[#D6E6F2] dark:from-[#0E0E34] dark:via-[#1A1A3A] dark:to-[#0E0E34] flex">
      <DashboardSidebar />

      <main className="flex-1 p-8 overflow-x-hidden">
        <div className="max-w-7xl mx-auto">
          {children}
        </div>
      </main>

      {/* Dashboard Modals */}
      <EditTaskModal />
      <DeleteConfirmModal />
    </div>
  )
}
