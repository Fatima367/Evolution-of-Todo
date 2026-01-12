'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Mail, Lock, User, UserPlus } from 'lucide-react'
import { useAuth } from '@/contexts/auth'
import { useUIStore } from '@/store'
import { Button } from '../ui/Button'
import { Input } from '../ui/Input'

export function SignUpModal() {
  const { isSignUpModalOpen, closeSignUpModal } = useUIStore()
  const { register } = useAuth()
  const router = useRouter()

  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await register({ name, email, password })
      closeSignUpModal()
      router.push('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <AnimatePresence>
      {isSignUpModalOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeSignUpModal}
            className="fixed inset-0 bg-black/50 backdrop-blur-md z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="glass-card p-8 rounded-2xl w-full max-w-md relative"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={closeSignUpModal}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>

              <div className="text-center mb-6">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] bg-clip-text text-transparent">
                  Get Started
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mt-2">
                  Create your free account
                </p>
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg dark:bg-red-900/20 dark:border-red-800"
                >
                  {error}
                </motion.div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  label="Name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  placeholder="John Doe"
                  leftIcon={<User className="h-4 w-4" />}
                />

                <Input
                  label="Email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="you@example.com"
                  leftIcon={<Mail className="h-4 w-4" />}
                />

                <Input
                  label="Password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="At least 8 characters"
                  leftIcon={<Lock className="h-4 w-4" />}
                />

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full glow-blue"
                  size="lg"
                >
                  {loading ? (
                    'Creating account...'
                  ) : (
                    <>
                      <UserPlus className="h-4 w-4 mr-2" />
                      Sign Up
                    </>
                  )}
                </Button>
              </form>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
