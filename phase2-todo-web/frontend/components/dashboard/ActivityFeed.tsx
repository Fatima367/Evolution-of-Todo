'use client'

import { motion } from 'framer-motion'
import { CheckCircle, Circle, Clock, AlertCircle, Activity } from 'lucide-react'
import { Card } from '../ui/Card'
import { formatRelativeDate } from '@/lib/utils/dateUtils'
import { Task } from '@/lib/types'

interface ActivityFeedProps {
  tasks?: Task[]
}

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

export function ActivityFeed({ tasks = [] }: ActivityFeedProps) {
  // Create activity log from tasks based on their status and timestamps
  const activities = tasks
    .map(task => {
      let type: 'created' | 'completed' | 'updated' | 'deleted' = 'created'

      // Determine activity type based on task properties
      if (task.completed_at) {
        type = 'completed'
      } else if (task.updated_at && new Date(task.updated_at).getTime() > new Date(task.created_at).getTime()) {
        type = 'updated'
      } else {
        type = 'created'
      }

      return {
        id: task.id,
        type,
        title: task.title,
        timestamp: new Date(task.updated_at || task.created_at),
      }
    })
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()) // Sort by most recent
    .slice(0, 4) // Limit to 4 most recent activities

  return (
    <Card className="glass-card p-6">
      <h3 className="text-lg font-semibold mb-4 dark:text-[#F7F6F7]">Recent Activity</h3>

      {activities.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Activity className="h-12 w-12 text-gray-400 mb-4 dark:text-[#C8C8D8]" />
          <h4 className="text-lg font-medium text-gray-500 dark:text-[#C8C8D8]">No recent activity</h4>
          <p className="text-sm text-gray-500 max-w-xs dark:text-[#C8C8D8]">
            Your recent task activities will appear here
          </p>
        </div>
      ) : (
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
                  <p className="text-sm text-gray-900 dark:text-[#F7F6F7]">
                    <span className="text-gray-500 dark:text-[#C8C8D8]">{config.text}</span>
                    {' "'}
                    <span className="font-medium">{activity.title}</span>
                    {'"'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-[#C8C8D8] mt-1">
                    {formatRelativeDate(activity.timestamp)}
                  </p>
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
