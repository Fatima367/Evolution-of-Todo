'use client'

import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  LayoutDashboard,
  CheckSquare,
  Settings,
  LogOut,
  X,
  ChevronLeft,
  ChevronRight,
  User
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store'
import { Button } from '../ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/dashboard/tasks', icon: CheckSquare },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export function DashboardSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuth()
  const { isSidebarOpen, toggleSidebar, setSidebarOpen } = useUIStore()

  const handleLogout = async () => {
    await logout()
  }

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          x: isSidebarOpen ? 0 : -300,
          width: isSidebarOpen ? 280 : 0,
        }}
        transition={{ duration: 0.3, ease: 'easeInOut' }}
        className="fixed left-0 top-0 h-screen bg-white/95 dark:bg-[#1A1A3A] border-r border-[#BAD0CC] dark:border-[#3A3A4A] z-50 lg:sticky lg:top-0 backdrop-blur-xl"
      >
        <div className="flex flex-col h-full p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <CheckSquare className="h-8 w-8 text-[#6EB8E1]" />
              <span className="text-xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] bg-clip-text text-transparent">
                TodoEvo
              </span>
            </Link>

            {/* Close button (mobile) / Collapse button (desktop) */}
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors lg:hidden"
            >
              <X className="h-5 w-5 text-gray-600 dark:text-gray-400" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')

              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`
                    flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-300
                    ${isActive
                      ? 'bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] text-white shadow-lg'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-[#D6E6F2] dark:hover:bg-[#252E8A]/40'
                    }
                  `}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              )
            })}
          </nav>

          {/* User Section */}
          <div className="border-t border-gray-200 dark:border-gray-700 pt-4 space-y-4">
            <div className="flex items-center space-x-3 px-4 py-3 rounded-lg bg-gray-50 dark:bg-[#252E3F]/30">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-[#6EB8E1] to-[#4EB5A9] flex items-center justify-center text-white font-semibold">
                {user?.name?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate text-gray-900 dark:text-gray-100">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {user?.email || 'user@example.com'}
                </p>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={handleLogout}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </motion.aside>

      {/* Desktop Collapse Toggle */}
      <button
        onClick={toggleSidebar}
        className="hidden lg:block fixed left-4 top-4 z-50 p-2 rounded-lg bg-white/90 dark:bg-[#1A1A3A] border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-all duration-300 hover:scale-105"
      >
        {isSidebarOpen ? (
          <ChevronLeft className="h-5 w-5 text-gray-600 dark:text-gray-400" />
        ) : (
          <ChevronRight className="h-5 w-5 text-gray-600 dark:text-gray-400" />
        )}
      </button>
    </>
  )
}
