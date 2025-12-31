'use client'

import { motion } from 'framer-motion'
import { Card } from '../ui/Card'
import { Target } from 'lucide-react'
import { Task } from '@/lib/types'

interface ProgressOverviewProps {
  tasks?: Task[]
}

const colorMap: Record<string, { bg: string; fill: string }> = {
  blue: { bg: 'bg-blue-200 dark:bg-[#6EB8E1]/30', fill: 'bg-blue-600 dark:bg-[#5A7FC8]' },
  purple: { bg: 'bg-purple-200 dark:bg-[#C8ABE6]/30', fill: 'bg-purple-600 dark:bg-[#201761]' },
  green: { bg: 'bg-green-200 dark:bg-[#BAD0CC]/30', fill: 'bg-green-600 dark:bg-[#4EB5A9]' },
  pink: { bg: 'bg-pink-200 dark:bg-[#FBE5E7]/30', fill: 'bg-pink-600 dark:bg-[#F8CEC0]' },
}

export function ProgressOverview({ tasks = [] }: ProgressOverviewProps) {
  // Function to assign a color based on category name
  const getCategoryColor = (category: string): 'blue' | 'purple' | 'green' | 'pink' => {
    const colors: ('blue' | 'purple' | 'green' | 'pink')[] = ['blue', 'purple', 'green', 'pink']
    // Use hash of category name to consistently assign a color
    let hash = 0
    for (let i = 0; i < category.length; i++) {
      hash = category.charCodeAt(i) + ((hash << 5) - hash)
    }
    return colors[Math.abs(hash) % colors.length]
  }

  // Group tasks by tags as categories (using first tag or 'Uncategorized' if no tags)
  const categories = Array.from(
    new Set(tasks.flatMap(task => task.tags && task.tags.length > 0 ? task.tags : ['Uncategorized']))
  ).map(category => {
    const categoryTasks = tasks.filter(task =>
      task.tags && task.tags.includes(category) || (category === 'Uncategorized' && (!task.tags || task.tags.length === 0))
    )
    const completed = categoryTasks.filter(task => task.status === 'completed').length

    return {
      category,
      completed,
      total: categoryTasks.length,
      color: getCategoryColor(category),
    }
  })

  return (
    <Card className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold dark:text-[#F7F6F7]">Progress Overview</h3>
          <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">
            Track your progress across categories
          </p>
        </div>
        <Target className="h-5 w-5 text-gray-400 dark:text-[#C8C8D8]" />
      </div>

      {categories.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <Target className="h-12 w-12 text-gray-400 dark:text-[#C8C8D8] mb-4" />
          <h4 className="text-lg font-medium text-gray-500 dark:text-[#C8C8D8]">No progress data</h4>
          <p className="text-sm text-gray-500 dark:text-[#C8C8D8] max-w-xs">
            Add tasks to different categories to track your progress
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map((item, index) => {
            const percentage = item.total > 0 ? Math.round((item.completed / item.total) * 100) : 0
            const colors = colorMap[item.color]

            return (
              <motion.div
                key={item.category}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium dark:text-[#F7F6F7]">{item.category}</span>
                  <span className="text-sm text-gray-500 dark:text-[#C8C8D8]">
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
                  <span className="text-xs text-gray-500 dark:text-[#C8C8D8]">{percentage}% complete</span>
                  {percentage === 100 && (
                    <span className="text-xs text-green-600 dark:text-[#4EB5A9] font-medium">✓ Done!</span>
                  )}
                </div>
              </motion.div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
