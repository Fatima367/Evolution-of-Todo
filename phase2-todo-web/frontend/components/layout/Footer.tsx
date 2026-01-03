'use client'

import Link from 'next/link'
import { FaGithub, FaTwitter, FaLinkedin, FaDiscord } from 'react-icons/fa'
import { CheckSquare } from 'lucide-react'

export function Footer() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="glass-card border-t border-white/20 dark:border-[#252E8A]/20 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <CheckSquare className="h-8 w-8 text-primary dark:text-[#6EB8E1]" />
              <span className="text-xl font-display font-bold bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent dark:from-[#6EB8E1] dark:via-[#48ADB7] dark:to-[#6EB8E1]">
                TodoBoard
              </span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              The last todo app you'll ever need. From simple lists to intelligent insights.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="GitHub"
              >
                <FaGithub className="h-5 w-5" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="Twitter"
              >
                <FaTwitter className="h-5 w-5" />
              </a>
              <a
                href="https://linkedin.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="LinkedIn"
              >
                <FaLinkedin className="h-5 w-5" />
              </a>
              <a
                href="https://discord.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                aria-label="Discord"
              >
                <FaDiscord className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              Product
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/#features"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Features
                </Link>
              </li>
              <li>
                <Link
                  href="/pricing"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Pricing
                </Link>
              </li>
              <li>
                <Link
                  href="/roadmap"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Roadmap
                </Link>
              </li>
              <li>
                <Link
                  href="/changelog"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Changelog
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              Company
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/about"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  About
                </Link>
              </li>
              <li>
                <Link
                  href="/blog"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Blog
                </Link>
              </li>
              <li>
                <Link
                  href="/careers"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Careers
                </Link>
              </li>
              <li>
                <Link
                  href="/contact"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Contact
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-4">
              Legal
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link
                  href="/privacy"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/terms"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link
                  href="/cookies"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Cookie Policy
                </Link>
              </li>
              <li>
                <Link
                  href="/security"
                  className="text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-[#6EB8E1] transition-colors"
                >
                  Security
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-12 pt-8 border-t border-gray-200 dark:border-gray-800">
          <p className="text-center text-sm text-gray-600 dark:text-gray-400">
            © {currentYear} TodoBoard. All rights reserved. Built with ❤️ for productivity.
          </p>
        </div>
      </div>
    </footer>
  )
}
