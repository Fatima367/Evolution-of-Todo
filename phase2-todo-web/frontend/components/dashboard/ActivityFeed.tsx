'use client'

import { motion } from 'framer-motion'
import { CheckCircle, Circle, Clock, AlertCircle } from 'lucide-react'
import { Card } from '../ui/Card'
import { formatRelativeDate } from '@/lib/utils/dateUtils'

interface Activity {
  id: string
  type: 'created' | 'completed' | 'updated' | 'deleted'
  title: string
  timestamp: Date
}

interface ActivityFeedProps {
  activities?: Activity[]
}

// Mock activities
const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'completed',
    title: 'Deploy to Vercel',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 mins ago
  },
  {
    id: '2',
    type: 'created',
    title: 'Review pull request #123',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
  },
  {
    id: '3',
    type: 'updated',
    title: 'Update documentation',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 5), // 5 hours ago
  },
  {
    id: '4',
    type: 'completed',
    title: 'Fix authentication bug',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
  },
]

const activityConfig = {
  created: {
    icon: Circle,
    color: 'text-blue-600',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    text: 'You created',
  },
  completed: {
    icon: CheckCircle,
    color: 'text-green-600',
    bg: 'bg-green-100 dark:bg-green-900/30',
    text: 'You completed',
  },
  updated: {
    icon: Clock,
    color: 'text-yellow-600',
    bg: 'bg-yellow-100 dark:bg-yellow-900/30',
    text: 'You updated',
  },
  deleted: {
    icon: AlertCircle,
    color: 'text-red-600',
    bg: 'bg-red-100 dark:bg-red-900/30',
    text: 'You deleted',
  },
}

export function ActivityFeed({ activities = mockActivities }: ActivityFeedProps) {
  return (
    <Card className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>

      <div className="space-y-4">
        {activities.map((activity, index) => {
          const config = activityConfig[activity.type]
          const Icon = config.icon

          return (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="flex items-start space-x-3"
            >
              <div className={`${config.bg} p-2 rounded-full flex-shrink-0`}>
                <Icon className={`h-4 w-4 ${config.color}`} />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-900 dark:text-gray-100">
                  <span className="text-gray-500 dark:text-gray-400">{config.text}</span>
                  {' "'}
                  <span className="font-medium">{activity.title}</span>
                  {'"'}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {formatRelativeDate(activity.timestamp)}
                </p>
              </div>
            </motion.div>
          )
        })}
      </div>
    </Card>
  )
}
