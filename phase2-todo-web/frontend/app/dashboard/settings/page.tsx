'use client'

import { motion } from 'framer-motion'
import { useState } from 'react'
import { User, Mail, Lock, Bell, Moon, Sun } from 'lucide-react'
import { useAuthStore, useUIStore } from '@/store'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const { theme, toggleTheme } = useUIStore()
  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement profile update API call
    console.log('Saving profile:', { name, email })
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your account and preferences
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Settings */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Profile Settings
            </h2>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                leftIcon={<User className="h-4 w-4" />}
              />

              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                leftIcon={<Mail className="h-4 w-4" />}
              />

              <Button type="submit" className="w-full glow-blue">
                Save Changes
              </Button>
            </form>
          </Card>
        </motion.div>

        {/* Theme Settings */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <Card className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              {theme === 'dark' ? (
                <Moon className="h-5 w-5 mr-2" />
              ) : (
                <Sun className="h-5 w-5 mr-2" />
              )}
              Appearance
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Theme</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Choose your preferred theme
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={toggleTheme}
                  className="flex items-center space-x-2"
                >
                  {theme === 'dark' ? (
                    <>
                      <Sun className="h-4 w-4" />
                      <span>Light</span>
                    </>
                  ) : (
                    <>
                      <Moon className="h-4 w-4" />
                      <span>Dark</span>
                    </>
                  )}
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Notifications */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <Card className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <Bell className="h-5 w-5 mr-2" />
              Notifications
            </h2>

            <div className="space-y-4">
              {[
                { label: 'Email Notifications', description: 'Receive updates via email' },
                { label: 'Task Reminders', description: 'Get reminded about upcoming tasks' },
                { label: 'Weekly Summary', description: 'Weekly productivity reports' },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{item.label}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {item.description}
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Security */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <Card className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center">
              <Lock className="h-5 w-5 mr-2" />
              Security
            </h2>

            <div className="space-y-4">
              <Button variant="outline" className="w-full">
                Change Password
              </Button>
              <Button variant="outline" className="w-full text-red-600 border-red-600 hover:bg-red-50 dark:hover:bg-red-900/20">
                Delete Account
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
