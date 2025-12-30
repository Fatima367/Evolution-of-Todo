'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card } from '../ui/Card'
import { TrendingUp } from 'lucide-react'
import { Task } from '@/lib/types'
import { useEffect } from 'react'

interface TaskCompletionChartProps {
  tasks?: Task[]
}

// Generate data for last 7 days
const generateLast7DaysData = () => {
  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const today = new Date()
  const data = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)

    data.push({
      date: days[date.getDay()],
      completed: 0
    })
  }

  return data
}

export function TaskCompletionChart({ tasks = [] }: TaskCompletionChartProps) {
  // Update chart colors based on theme
  useEffect(() => {
    const updateChartColors = () => {
      const isDark = document.documentElement.classList.contains('dark')
      const chartElements = document.querySelectorAll('.recharts-cartesian-axis-line, .recharts-cartesian-axis-tick-line')

      chartElements.forEach(el => {
        if (el instanceof SVGElement) {
          el.setAttribute('stroke', isDark ? '#C8C8D8' : '#9ca3af')
        }
      })

      const tickElements = document.querySelectorAll('.recharts-cartesian-axis-tick-value')
      tickElements.forEach(el => {
        if (el instanceof SVGTextElement) {
          el.setAttribute('fill', isDark ? '#C8C8D8' : '#9ca3af')
        }
      })
    }

    updateChartColors()
    window.addEventListener('themeChange', updateChartColors)

    return () => {
      window.removeEventListener('themeChange', updateChartColors)
    }
  }, [])
  // Filter completed tasks from the last 7 days
  const last7DaysData = generateLast7DaysData()

  // Update the data with actual completed tasks
  const completedTasksByDay = tasks
    .filter(task => task.status === 'completed') // Only completed tasks
    .reduce((acc, task) => {
      // Use completed_at if available, otherwise use updated_at
      const completionDate = task.completed_at || task.updated_at || task.created_at
      const taskDate = new Date(completionDate)
      const dayOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][taskDate.getDay()]

      const dayEntry = acc.find(entry => entry.date === dayOfWeek)
      if (dayEntry) {
        dayEntry.completed += 1
      }

      return acc
    }, [...last7DaysData])

  const total = completedTasksByDay.reduce((sum, item) => sum + item.completed, 0)

  return (
    <Card className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold dark:text-[#F7F6F7]">Task Completion</h3>
          <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">Last 7 days</p>
        </div>
        <div className="flex items-center space-x-2 text-green-600 dark:text-[#4EB5A9]">
          <TrendingUp className="h-5 w-5" />
          <span className="text-2xl font-bold">{total}</span>
        </div>
      </div>

      {total === 0 ? (
        <div className="flex flex-col items-center justify-center h-[250px] text-center">
          <TrendingUp className="h-12 w-12 text-gray-400 mb-4 dark:text-[#C8C8D8]" />
          <h4 className="text-lg font-medium text-gray-500 dark:text-[#C8C8D8]">No completed tasks</h4>
          <p className="text-sm text-gray-500 max-w-xs dark:text-[#C8C8D8]">
            Complete tasks to see your progress over the last 7 days
          </p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={completedTasksByDay}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
            <XAxis
              dataKey="date"
              stroke="#9ca3af"
              style={{ fontSize: '12px' }}
            />
            <YAxis stroke="#9ca3af" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                border: 'none',
                borderRadius: '8px',
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                color: '#0E0E34',
              }}
            />
            <Line
              type="monotone"
              dataKey="completed"
              stroke="url(#colorGradient)"
              strokeWidth={3}
              dot={{ fill: '#3B82F6', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <defs>
              <linearGradient id="colorGradient" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#A855F7" />
              </linearGradient>
            </defs>
          </LineChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
