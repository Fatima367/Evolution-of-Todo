'use client'

import { motion } from 'framer-motion'
import { Card } from '../ui/Card'
import { Target } from 'lucide-react'

interface Progress {
  category: string
  completed: number
  total: number
  color: string
}

interface ProgressOverviewProps {
  progress?: Progress[]
}

// Mock data
const mockProgress: Progress[] = [
  { category: 'Work Projects', completed: 12, total: 15, color: 'blue' },
  { category: 'Personal Goals', completed: 8, total: 10, color: 'purple' },
  { category: 'Learning', completed: 5, total: 12, color: 'green' },
  { category: 'Health & Fitness', completed: 7, total: 7, color: 'pink' },
]

const colorMap: Record<string, { bg: string; fill: string }> = {
  blue: { bg: 'bg-blue-200 dark:bg-blue-900/30', fill: 'bg-blue-600' },
  purple: { bg: 'bg-purple-200 dark:bg-purple-900/30', fill: 'bg-purple-600' },
  green: { bg: 'bg-green-200 dark:bg-green-900/30', fill: 'bg-green-600' },
  pink: { bg: 'bg-pink-200 dark:bg-pink-900/30', fill: 'bg-pink-600' },
}

export function ProgressOverview({ progress = mockProgress }: ProgressOverviewProps) {
  return (
    <Card className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Progress Overview</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Track your progress across categories
          </p>
        </div>
        <Target className="h-5 w-5 text-gray-400" />
      </div>

      <div className="space-y-4">
        {progress.map((item, index) => {
          const percentage = Math.round((item.completed / item.total) * 100)
          const colors = colorMap[item.color]

          return (
            <motion.div
              key={item.category}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">{item.category}</span>
                <span className="text-sm text-gray-500">
                  {item.completed}/{item.total}
                </span>
              </div>

              <div className={`w-full h-2 ${colors.bg} rounded-full overflow-hidden`}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 1, delay: index * 0.1 + 0.3 }}
                  className={`h-full ${colors.fill} rounded-full`}
                />
              </div>

              <div className="flex items-center justify-between mt-1">
                <span className="text-xs text-gray-500">{percentage}% complete</span>
                {percentage === 100 && (
                  <span className="text-xs text-green-600 font-medium">✓ Done!</span>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </Card>
  )
}
