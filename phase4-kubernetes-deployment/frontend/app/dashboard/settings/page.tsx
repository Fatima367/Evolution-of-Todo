'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'
import { User, Mail, Lock, Bell, Moon, Sun, AlertCircle } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store'
import { Card } from '@/components/ui/Card'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { apiClient } from '@/lib/api'

export default function SettingsPage() {
  const { user, updateUser, logout } = useAuth()
  const { theme, toggleTheme } = useUIStore()
  const [name, setName] = useState(user?.name || '')
  const [email, setEmail] = useState(user?.email || '')
  const [notificationSettings, setNotificationSettings] = useState({
    email_notifications: user?.email_notifications ?? true,
    task_reminders: user?.task_reminders ?? true,
    weekly_summary: user?.weekly_summary ?? true,
  })
  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false)
  const [isUpdatingNotifications, setIsUpdatingNotifications] = useState(false)
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmNewPassword, setConfirmNewPassword] = useState('')
  const [isUpdatingPassword, setIsUpdatingPassword] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletePassword, setDeletePassword] = useState('')
  const [isDeletingAccount, setIsDeletingAccount] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Initialize form with user data when user changes
  useEffect(() => {
    if (user) {
      setName(user.name || '')
      setEmail(user.email || '')
      setNotificationSettings({
        email_notifications: user.email_notifications ?? true,
        task_reminders: user.task_reminders ?? true,
        weekly_summary: user.weekly_summary ?? true,
      })
    }
  }, [user])

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUpdatingProfile(true)
    setError(null)
    setSuccess(null)

    try {
      const updatedUser = await apiClient.updateCurrentUser({ name })
      updateUser(updatedUser)
      setSuccess('Profile updated successfully!')
    } catch (err) {
      console.error('Error updating profile:', err)
      setError('Failed to update profile. Please try again.')
    } finally {
      setIsUpdatingProfile(false)
    }
  }

  const handleNotificationChange = async (setting: keyof typeof notificationSettings) => {
    const newSettings = {
      ...notificationSettings,
      [setting]: !notificationSettings[setting]
    }
    setNotificationSettings(newSettings)
    setIsUpdatingNotifications(true)
    setError(null)
    setSuccess(null)

    try {
      const updatedUser = await apiClient.updateCurrentUser({ [setting]: newSettings[setting] })
      updateUser(updatedUser)
      setSuccess('Notification settings updated successfully!')
    } catch (err) {
      console.error('Error updating notification settings:', err)
      setError('Failed to update notification settings. Please try again.')
      // Revert the change in case of error
      setNotificationSettings((prev) => prev)
    } finally {
      setIsUpdatingNotifications(false)
    }
  }

  const handleChangePassword = () => {
    setShowPasswordModal(true)
    // TODO: Implement change password functionality
  }

  const handleDeleteAccount = () => {
    setShowDeleteModal(true)
    // TODO: Implement delete account functionality
  }

  const handleConfirmPasswordChange = async () => {
    // Basic validation
    if (!currentPassword || !newPassword || !confirmNewPassword) {
      setError('Please fill in all password fields.')
      return
    }

    if (newPassword !== confirmNewPassword) {
      setError('New passwords do not match.')
      return
    }

    if (newPassword.length < 8) {
      setError('New password must be at least 8 characters long.')
      return
    }

    setIsUpdatingPassword(true)
    setError(null)
    setSuccess(null)

    try {
      await apiClient.changePassword(currentPassword, newPassword)
      setSuccess('Password changed successfully!')
      setShowPasswordModal(false)
      // Reset form
      setCurrentPassword('')
      setNewPassword('')
      setConfirmNewPassword('')
    } catch (err: any) {
      console.error('Error changing password:', err)
      setError(err.message || 'Failed to change password. Please try again.')
    } finally {
      setIsUpdatingPassword(false)
    }
  }

  const handleConfirmDeleteAccount = async () => {
    if (!deletePassword) {
      setError('Please enter your password to confirm account deletion.')
      return
    }

    setIsDeletingAccount(true)
    setError(null)
    setSuccess(null)

    try {
      await apiClient.deleteAccount(deletePassword)
      setSuccess('Account deleted successfully.')
      setShowDeleteModal(false)
      setDeletePassword('')
      // Log out the user after account deletion
      setTimeout(() => {
        // This will trigger the logout process
        logout() // Use the logout function from auth context
      }, 1500)
    } catch (err: any) {
      console.error('Error deleting account:', err)
      setError(err.message || 'Failed to delete account. Please try again.')
    } finally {
      setIsDeletingAccount(false)
    }
  }

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your account and preferences
        </p>
      </motion.div>

      {/* Success/Error Messages */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center"
        >
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <span className="text-red-700 dark:text-red-300">{error}</span>
        </motion.div>
      )}
      {success && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-center"
        >
          <AlertCircle className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-700 dark:text-green-300">{success}</span>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Profile Settings */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card className="glass-card p-6">
            <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900 dark:text-[#F7F6F7]">
              <User className="h-5 w-5 mr-2 text-[#6EB8E1]" />
              Profile Settings
            </h2>

            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                leftIcon={<User className="h-4 w-4 text-gray-400 dark:text-gray-500" />}
              />

              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                leftIcon={<Mail className="h-4 w-4 text-gray-400 dark:text-gray-500" />}
                disabled
              />

              <Button
                type="submit"
                className="w-full glow-blue"
                disabled={isUpdatingProfile || name === (user?.name || '')}
              >
                {isUpdatingProfile ? 'Saving...' : 'Save Changes'}
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
            <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900 dark:text-[#F7F6F7]">
              {theme === 'dark' ? (
                <Moon className="h-5 w-5 mr-2 text-[#C8ABE6]" />
              ) : (
                <Sun className="h-5 w-5 mr-2 text-[#6EB8E1]" />
              )}
              Appearance
            </h2>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-[#F7F6F7]">Theme</p>
                  <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">
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
            <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900 dark:text-[#F7F6F7]">
              <Bell className="h-5 w-5 mr-2 text-[#F59E0B]" />
              Notifications
            </h2>

            <div className="space-y-4">
              {[
                { key: 'email_notifications', label: 'Email Notifications', description: 'Receive updates via email' },
                { key: 'task_reminders', label: 'Task Reminders', description: 'Get reminded about upcoming tasks' },
                { key: 'weekly_summary', label: 'Weekly Summary', description: 'Weekly productivity reports' },
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-[#F7F6F7]">{item.label}</p>
                    <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">
                      {item.description}
                    </p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={notificationSettings[item.key as keyof typeof notificationSettings]}
                      onChange={() => handleNotificationChange(item.key as keyof typeof notificationSettings)}
                    />
                    <div className={`w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 ${notificationSettings[item.key as keyof typeof notificationSettings] ? 'peer-checked:bg-blue-600 dark:peer-checked:bg-[#5A7FC8]' : ''}`}></div>
                  </label>
                </div>
              ))}
              {isUpdatingNotifications && (
                <p className="text-xs text-gray-500 dark:text-[#C8C8D8] text-right">Saving...</p>
              )}
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
            <h2 className="text-xl font-semibold mb-6 flex items-center text-gray-900 dark:text-[#F7F6F7]">
              <Lock className="h-5 w-5 mr-2 text-[#4EB5A9]" />
              Security
            </h2>

            <div className="space-y-4">
              <Button
                variant="outline"
                className="w-full"
                onClick={handleChangePassword}
              >
                Change Password
              </Button>
              <Button
                variant="outline"
                className="w-full text-red-600 border-red-600 hover:bg-red-100 dark:bg-red-900/40 dark:hover:bg-red-900/20 hover:text-red-500 dark:hover:text-red-600"
                onClick={handleDeleteAccount}
              >
                Delete Account
              </Button>
            </div>
          </Card>
        </motion.div>
      </div>

      {/* Password Change Modal */}
      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-semibold mb-4">Change Password</h3>
            {error && showPasswordModal && (
                <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-2 mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center"
              >
                <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                <span className="text-red-700 dark:text-red-300 text-sm">{error}</span>
              </motion.div>
            )}
            <form onSubmit={(e) => { e.preventDefault(); handleConfirmPasswordChange(); }}>
              <div className="space-y-4 mb-6">
                <Input
                  label="Current Password"
                  type="password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Enter current password"
                />
                <Input
                  label="New Password"
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                />
                <Input
                  label="Confirm New Password"
                  type="password"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  placeholder="Confirm new password"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowPasswordModal(false)
                    setCurrentPassword('')
                    setNewPassword('')
                    setConfirmNewPassword('')
                    setError(null)
                  }}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={isUpdatingPassword}
                >
                  {isUpdatingPassword ? 'Changing...' : 'Change Password'}
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md"
          >
            <h3 className="text-lg font-semibold mb-4 text-red-600">Delete Account</h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently removed.
            </p>
            <div className="mb-4">
              <Input
                label="Confirm Password"
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Enter your password to confirm"
              />
            </div>
            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowDeleteModal(false)
                  setDeletePassword('')
                }}
              >
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={handleConfirmDeleteAccount}
                disabled={isDeletingAccount}
              >
                {isDeletingAccount ? 'Deleting...' : 'Delete Account'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}
