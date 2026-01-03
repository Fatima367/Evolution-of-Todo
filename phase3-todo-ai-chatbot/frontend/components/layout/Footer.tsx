'use client'

import Link from 'next/link'
import { Github, Twitter, Linkedin, CheckSquare, Shield, FileText, LayoutDashboard, ListTodo, Settings, UserPlus, LogIn } from 'lucide-react'
import { useUIStore } from '@/store'
import { useAuth } from '@/hooks/useAuth'

export function Footer() {
  const currentYear = new Date().getFullYear()
  const { openSignUpModal, openLoginModal } = useUIStore()
  const { isAuthenticated } = useAuth()

  return (
    <footer className="glass-card border-t border-white/20 dark:border-[#252E8A]/20 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-12 md:gap-8">
          {/* Brand Section */}
          <div className="space-y-4 col-span-1 sm:col-span-2 md:col-span-1">
            <div className="flex items-center space-x-2 shrink-0">
              <CheckSquare className="h-8 w-8 text-primary dark:text-[#6EB8E1]" />
              <span className="text-xl font-display font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent dark:from-[#6EB8E1] dark:via-[#48ADB7] dark:to-[#6EB8E1]">
                TodoEvo
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs">
              The last todo app you'll ever need. From simple lists to intelligent insights.
            </p>
            <div className="flex space-x-4 pt-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* User Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
              Application
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/dashboard"
                  className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  <LayoutDashboard className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                  Dashboard
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard/tasks"
                  className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  <ListTodo className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                  My Tasks
                </Link>
              </li>
              <li>
                <Link
                  href="/dashboard/settings"
                  className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  <Settings className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                  Settings
                </Link>
              </li>
            </ul>
          </div>

          {/* Platform Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
              Account
            </h3>
            <ul className="space-y-3">
              {!isAuthenticated ? (
                <>
                  <li>
                    <button
                      onClick={openLoginModal}
                      className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors w-full text-left font-normal bg-transparent border-none p-0 cursor-pointer"
                    >
                      <LogIn className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                      Sign In
                    </button>
                  </li>
                  <li>
                    <button
                      onClick={openSignUpModal}
                      className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors w-full text-left font-normal bg-transparent border-none p-0 cursor-pointer"
                    >
                      <UserPlus className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                      Create Account
                    </button>
                  </li>
                </>
              ) : (
                <li className="text-sm text-gray-500 dark:text-gray-500 italic">
                  You are currently signed in
                </li>
              )}
            </ul>
          </div>

          {/* Legal Links */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider">
              Legal
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/privacy"
                  className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  <Shield className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="group flex items-center text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  <FileText className="h-4 w-4 mr-2 opacity-70 group-hover:opacity-100" />
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 pt-8 border-t border-gray-100 dark:border-gray-800 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <p className="text-sm text-gray-500 dark:text-gray-400 text-center md:text-left">
            © {currentYear} TodoEvo. All rights reserved. Built with ❤️ for productivity.
          </p>
          <div className="flex items-center space-x-2 text-xs text-gray-400 dark:text-gray-500">
            <span>Powered by</span>
            <span className="font-semibold text-gray-500 dark:text-gray-400 font-display">Next.js</span>
            <span>&</span>
            <span className="font-semibold text-gray-500 dark:text-gray-400 font-display">FastAPI</span>
          </div>
        </div>
      </div>
    </footer>
  )
}
