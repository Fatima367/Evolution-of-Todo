'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Card } from '../ui/Card'
import { AlertCircle } from 'lucide-react'

interface PriorityPieChartProps {
  data?: Array<{ name: string; value: number; color: string }>
}

// Mock data
const mockData = [
  { name: 'High', value: 15, color: '#EF4444' },
  { name: 'Medium', value: 25, color: '#F59E0B' },
  { name: 'Low', value: 30, color: '#10B981' },
  { name: 'Urgent', value: 10, color: '#A855F7' },
]

export function PriorityPieChart({ data = mockData }: PriorityPieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <Card className="glass-card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold">Tasks by Priority</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Total: {total} tasks
          </p>
        </div>
        <AlertCircle className="h-5 w-5 text-gray-400" />
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              borderRadius: '8px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            }}
          />
          <Legend
            verticalAlign="bottom"
            height={36}
            iconType="circle"
            formatter={(value, entry: any) => (
              <span className="text-sm">
                {value} ({entry.payload.value})
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
