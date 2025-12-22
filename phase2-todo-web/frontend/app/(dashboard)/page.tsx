'use client'

import { motion } from 'framer-motion'
import { useAuthStore } from '@/store'
import {
  TaskCompletionChart,
  PriorityPieChart,
  ActivityFeed,
  ProgressOverview,
} from '@/components/dashboard'
import { CheckCircle, Clock, AlertCircle, TrendingUp } from 'lucide-react'
import { Card } from '@/components/ui/Card'

const stats = [
  {
    name: 'Total Tasks',
    value: '80',
    change: '+12%',
    icon: CheckCircle,
    color: 'blue',
  },
  {
    name: 'In Progress',
    value: '15',
    change: '+5%',
    icon: Clock,
    color: 'yellow',
  },
  {
    name: 'Completed',
    value: '57',
    change: '+18%',
    icon: TrendingUp,
    color: 'green',
  },
  {
    name: 'High Priority',
    value: '8',
    change: '-3%',
    icon: AlertCircle,
    color: 'red',
  },
]

export default function DashboardPage() {
  const { user } = useAuthStore()

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          Welcome back, {user?.name || 'User'}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Here's what's happening with your tasks today
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="glass-card p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {stat.name}
                    </p>
                    <p className="text-3xl font-bold mt-2">{stat.value}</p>
                    <p className={`text-sm mt-2 ${
                      stat.change.startsWith('+') ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change} from last week
                    </p>
                  </div>
                  <div className={`p-3 rounded-xl bg-${stat.color}-100 dark:bg-${stat.color}-900/30`}>
                    <Icon className={`h-6 w-6 text-${stat.color}-600`} />
                  </div>
                </div>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <TaskCompletionChart />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <PriorityPieChart />
        </motion.div>
      </div>

      {/* Activity and Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <ActivityFeed />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <ProgressOverview />
        </motion.div>
      </div>
    </div>
  )
}
