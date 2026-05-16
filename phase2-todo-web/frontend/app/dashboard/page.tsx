'use client'

import { motion } from 'framer-motion'
import { useAuth } from '@/hooks/useAuth'
import { useTasks } from '@/hooks/useTasks'
import {
  TaskCompletionChart,
  PriorityPieChart,
  ActivityFeed,
  ProgressOverview,
} from '@/components/dashboard'
import { CheckCircle, Clock, AlertCircle, TrendingUp } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Loading'

// Helper to get start and end of current week (Sunday to Saturday)
const getCurrentWeekRange = () => {
  const today = new Date()
  const dayOfWeek = today.getDay() // 0 = Sunday, 6 = Saturday
  const startOfWeek = new Date(today)
  startOfWeek.setDate(today.getDate() - dayOfWeek)
  startOfWeek.setHours(0, 0, 0, 0)
  const endOfWeek = new Date(today)
  endOfWeek.setDate(today.getDate() + (6 - dayOfWeek))
  endOfWeek.setHours(23, 59, 59, 999)
  return { start: startOfWeek, end: endOfWeek }
}

// Helper to get start and end of previous week
const getPreviousWeekRange = () => {
  const { start, end } = getCurrentWeekRange()
  const startOfPrevWeek = new Date(start)
  startOfPrevWeek.setDate(start.getDate() - 7)
  startOfPrevWeek.setHours(0, 0, 0, 0)
  const endOfPrevWeek = new Date(end)
  endOfPrevWeek.setDate(end.getDate() - 7)
  endOfPrevWeek.setHours(23, 59, 59, 999)
  return { start: startOfPrevWeek, end: endOfPrevWeek }
}

// Helper to calculate percentage change
const calculatePercentageChange = (current: number, previous: number): string => {
  if (previous === 0) {
    return current > 0 ? '+100%' : '0%'
  }
  const change = ((current - previous) / previous) * 100
  const formattedChange = Math.round(change)
  return formattedChange >= 0 ? `+${formattedChange}%` : `${formattedChange}%`
}

// Helper to filter tasks by date range
const filterTasksByDateRange = (
  tasks: any[],
  startDate: Date,
  endDate: Date,
  filterFn?: (task: any) => boolean
) => {
  return tasks.filter(task => {
    const taskDate = new Date(task.created_at)
    const matchesDate = taskDate >= startDate && taskDate <= endDate
    const matchesFilter = filterFn ? filterFn(task) : true
    return matchesDate && matchesFilter
  })
}

const COLOR_MAP: Record<string, { bg: string; border: string; icon: string }> = {
  blue: { bg: '#D6E6F2', border: '#6EB8E1', icon: '#6EB8E1' },
  yellow: { bg: '#FEF3C7', border: '#F59E0B', icon: '#F59E0B' },
  green: { bg: '#D1FAE5', border: '#10B981', icon: '#10B981' },
  red: { bg: '#FEE2E2', border: '#EF4444', icon: '#EF4444' },
}

const getStatColors = (color: string) => COLOR_MAP[color] || COLOR_MAP.blue

export default function DashboardPage() {
  const { user } = useAuth()
  const { tasks, loading } = useTasks()

  // Calculate week-over-week stats
  const currentWeek = getCurrentWeekRange()
  const previousWeek = getPreviousWeekRange()

  // Current week stats
  const currentTotal = filterTasksByDateRange(tasks, currentWeek.start, currentWeek.end).length
  const currentPending = filterTasksByDateRange(tasks, currentWeek.start, currentWeek.end, task => task.status === 'pending').length
  const currentCompleted = filterTasksByDateRange(tasks, currentWeek.start, currentWeek.end, task => task.status === 'completed').length
  const currentHighPriority = filterTasksByDateRange(tasks, currentWeek.start, currentWeek.end, task => task.priority === 'high' || task.priority === 'urgent').length

  // Previous week stats
  const previousTotal = filterTasksByDateRange(tasks, previousWeek.start, previousWeek.end).length
  const previousPending = filterTasksByDateRange(tasks, previousWeek.start, previousWeek.end, task => task.status === 'pending').length
  const previousCompleted = filterTasksByDateRange(tasks, previousWeek.start, previousWeek.end, task => task.status === 'completed').length
  const previousHighPriority = filterTasksByDateRange(tasks, previousWeek.start, previousWeek.end, task => task.priority === 'high' || task.priority === 'urgent').length

  // Calculate percentage changes
  const totalChange = calculatePercentageChange(currentTotal, previousTotal)
  const pendingChange = calculatePercentageChange(currentPending, previousPending)
  const completedChange = calculatePercentageChange(currentCompleted, previousCompleted)
  const highPriorityChange = calculatePercentageChange(currentHighPriority, previousHighPriority)

  // Define stats configuration
  const statConfigs = [
    {
      name: 'Total Tasks',
      value: currentTotal,
      change: totalChange,
      icon: CheckCircle,
      color: 'blue',
    },
    {
      name: 'Pending',
      value: currentPending,
      change: pendingChange,
      icon: Clock,
      color: 'yellow',
    },
    {
      name: 'Completed',
      value: currentCompleted,
      change: completedChange,
      icon: TrendingUp,
      color: 'green',
    },
    {
      name: 'High Priority',
      value: currentHighPriority,
      change: highPriorityChange,
      icon: AlertCircle,
      color: 'red',
    },
  ]

  if (loading) {
    return (
      <div className="space-y-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] bg-clip-text text-transparent">
            Welcome back, {user?.name || 'User'}!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Here's what's happening with your tasks today
          </p>
        </motion.div>

        {/* Stats Grid Skeletons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((_, index) => (
            <div key={index}>
              <Skeleton className="h-32 w-full" />
            </div>
          ))}
        </div>

        {/* Charts Grid Skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 w-full" />
          <Skeleton className="h-80 w-full" />
        </div>

        {/* Activity and Progress Skeletons */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 w-full" />
          <Skeleton className="h-80 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] bg-clip-text text-transparent">
          Welcome back, {user?.name || 'User'}!
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Here's what's happening with your tasks today
        </p>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {statConfigs.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.name}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -4, scale: 1.02 }}
            >
              <Card className="bg-white dark:bg-[#1A1A3A] p-6 border-2 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300" style={{ borderColor: getStatColors(stat.color).border }}>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 dark:text-[#C8C8D8]">
                      {stat.name}
                    </p>
                    <p className="text-3xl font-bold mt-2 text-gray-900 dark:text-[#F7F6F7]">{stat.value}</p>
                    <p className={`text-sm mt-2 ${
                      stat.change.startsWith('+') ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                    }`}>
                      {stat.change} from last week
                    </p>
                  </div>
                  <div className={`p-3 rounded-xl transition-transform hover:scale-110`} style={{ backgroundColor: getStatColors(stat.color).bg }}>
                    <Icon className={`h-6 w-6`} style={{ color: getStatColors(stat.color).icon }} />
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
          whileHover={{ scale: 1.01 }}
        >
          <TaskCompletionChart tasks={tasks} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          whileHover={{ scale: 1.01 }}
        >
          <PriorityPieChart tasks={tasks} />
        </motion.div>
      </div>

      {/* Activity and Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          whileHover={{ scale: 1.01 }}
        >
          <ActivityFeed tasks={tasks} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          whileHover={{ scale: 1.01 }}
        >
          <ProgressOverview tasks={tasks} />
        </motion.div>
      </div>
    </div>
  )
}
