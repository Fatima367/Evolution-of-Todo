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

interface TaskCompletionChartProps {
  data?: Array<{ date: string; completed: number }>
}

// Mock data for last 7 days
const mockData = [
  { date: 'Mon', completed: 5 },
  { date: 'Tue', completed: 8 },
  { date: 'Wed', completed: 6 },
  { date: 'Thu', completed: 12 },
  { date: 'Fri', completed: 9 },
  { date: 'Sat', completed: 7 },
  { date: 'Sun', completed: 10 },
]

export function TaskCompletionChart({ data = mockData }: TaskCompletionChartProps) {
  const total = data.reduce((sum, item) => sum + item.completed, 0)

  return (
    <Card className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Task Completion</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Last 7 days</p>
        </div>
        <div className="flex items-center space-x-2 text-green-600">
          <TrendingUp className="h-5 w-5" />
          <span className="text-2xl font-bold">{total}</span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
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
    </Card>
  )
}
