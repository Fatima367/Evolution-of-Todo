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
  User,
  Calendar,
  Star
} from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store'
import { Button } from '../ui/Button'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tasks', href: '/dashboard/tasks', icon: CheckSquare },
  { name: 'Calendar', href: '/dashboard/calendar', icon: Calendar },
  { name: 'Favorites', href: '/dashboard/favorites', icon: Star },
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
        className="fixed left-0 top-0 h-screen bg-white/80 dark:bg-[#0E0E34]/95 border-r border-[#BAD0CC]/50 dark:border-[#252E8A]/50 z-50 lg:sticky lg:top-0 backdrop-blur-2xl"
      >
        <div className="flex flex-col h-full p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <Link href="/dashboard" className="flex items-center space-x-3">
              <div className="relative">
                <div className="absolute inset-0 blur-lg opacity-50 rounded-xl" />
                <CheckSquare className="h-8 w-8 text-[#6EB8E1] relative" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] bg-clip-text text-transparent">
                TodoBoard
              </span>
            </Link>

            {/* Close button (mobile) / Collapse button (desktop) */}
            <button
              onClick={toggleSidebar}
              className="p-2 rounded-lg hover:bg-gray-100/80 dark:hover:bg-gray-700/50 transition-colors lg:hidden"
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
                    group relative flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300
                    ${isActive
                      ? 'bg-gradient-to-r from-[#6EB8E1] to-[#7be1d5] dark:from-[#252E8A]/50 dark:to-[#1A1A3A]/50 border border-[#6EB8E1]/30 dark:border-[#4EB5A9]/30'
                      : 'hover:bg-gray-100/60 dark:hover:bg-gray-800/40 border border-transparent'
                    }
                  `}
                >
                  {/* Active indicator */}
                  {isActive && (
                    <>
                      <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-[#6EB8E1] to-[#4EB5A9] rounded-r-full shadow-[0_0_10px_rgba(110,184,225,0.5)]" />
                      <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-[#6EB8E1]/10 to-[#4EB5A9]/10 blur-md" />
                    </>
                  )}

                  {/* Icon with glow effect */}
                  <div className={`
                    relative p-2 rounded-lg transition-all duration-300
                    ${isActive
                      ? 'bg-transparent dark:bg-[#4EB5A9]/20'
                      : 'group-hover:bg-gray-100 dark:group-hover:bg-gray-800'
                    }
                  `}>
                    <Icon className={`
                      h-5 w-5 transition-all duration-300
                      ${isActive
                        ? 'text-white dark:text-[#4EB5A9] drop-shadow-[0_0_8px_rgba(110,184,225,0.5)]'
                        : 'text-gray-500 dark:text-gray-400 group-hover:text-[#6EB8E1] dark:group-hover:text-[#4EB5A9]'
                      }
                    `} />
                  </div>

                  <span className={`
                    font-medium transition-all duration-300 z-10
                    ${isActive
                      ? 'text-white'
                      : 'text-gray-600 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white'
                    }
                  `}>
                    {item.name}
                  </span>

                  {/* Hover glow effect */}
                  {!isActive && (
                    <div className="absolute inset-0 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-gradient-to-r from-[#6EB8E1]/5 to-[#4EB5A9]/5 blur-md" />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* User Section */}
          <div className="border-t border-[#BAD0CC]/50 dark:border-[#252E8A]/50 pt-4 space-y-4">
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

      {/* Mobile Toggle Button - appears when sidebar is closed on small screens */}
      {!isSidebarOpen && (
        <button
          onClick={toggleSidebar}
          className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-white/90 dark:bg-[#1A1A3A] border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-all duration-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-600 dark:text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      )}
    </>
  )
}
