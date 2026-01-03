'use client'

import { useState } from 'react'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import { Menu, X, CheckSquare } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store'
import { Button } from '../ui/Button'

export function Navbar() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const { isAuthenticated, logout } = useAuth()
  const { openSignUpModal, openLoginModal } = useUIStore()

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/20 dark:border-[#5A7FC8]/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2 group">
            <div className="relative">
              <CheckSquare className="h-8 w-8 text-primary dark:text-[#6EB8E1] transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 glow-primary blur-xl opacity-0 group-hover:opacity-100 transition-opacity dark:glow-[#5A7FC8]" />
            </div>
            <span className="text-xl font-display font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent dark:from-[#6EB8E1] dark:via-[#48ADB7] dark:to-[#6EB8E1]">
              TodoBoard
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-gray-700 dark:text-[#C8C8D8] hover:text-primary dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href="/dashboard/tasks"
                  className="text-gray-700 dark:text-[#C8C8D8] hover:text-primary dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Tasks
                </Link>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={async () => {
                    await logout()
                    window.location.href = '/'
                  }}
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={openLoginModal}
                >
                  Login
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={openSignUpModal}
                  className="glow-primary bg-primary hover:bg-primary/90 dark:from-[#6EB8E1] dark:to-[#5A7FC8]"
                >
                  Sign Up
                </Button>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden p-2 rounded-lg hover:bg-gray-200/50 dark:hover:bg-[#5A7FC8]/30 transition-colors"
            aria-label="Toggle menu"
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6 text-gray-700 dark:text-[#C8C8D8]" />
            ) : (
              <Menu className="h-6 w-6 text-gray-700 dark:text-[#C8C8D8]" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="md:hidden glass-card border-t border-white/20 dark:border-[#5A7FC8]/30"
          >
            <div className="px-4 py-4 space-y-3">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/dashboard"
                    className="block px-4 py-2 rounded-lg hover:bg-gray-200/50 dark:hover:bg-[#5A7FC8]/30 transition-colors text-gray-700 dark:text-[#C8C8D8]"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/dashboard/tasks"
                    className="block px-4 py-2 rounded-lg hover:bg-gray-200/50 dark:hover:bg-[#5A7FC8]/30 transition-colors text-gray-700 dark:text-[#C8C8D8]"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Tasks
                  </Link>
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={async () => {
                      await logout()
                      setIsMobileMenuOpen(false)
                      window.location.href = '/'
                    }}
                  >
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="ghost"
                    className="w-full"
                    onClick={() => {
                      openLoginModal()
                      setIsMobileMenuOpen(false)
                    }}
                  >
                    Login
                  </Button>
                  <Button
                    variant="primary"
                    className="w-full glow-primary bg-primary hover:bg-primary/90 dark:from-[#6EB8E1] dark:to-[#5A7FC8]"
                    onClick={() => {
                      openSignUpModal()
                      setIsMobileMenuOpen(false)
                    }}
                  >
                    Sign Up
                  </Button>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
