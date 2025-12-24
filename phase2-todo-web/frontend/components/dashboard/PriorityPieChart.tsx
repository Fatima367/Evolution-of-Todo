'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { Card } from '../ui/Card'
import { AlertCircle, Clock } from 'lucide-react'
import { Task } from '@/lib/types'

interface PriorityPieChartProps {
  tasks?: Task[]
}

export function PriorityPieChart({ tasks = [] }: PriorityPieChartProps) {
  // Calculate priority distribution
  const priorityData = [
    { name: 'High', value: tasks.filter(t => t.priority === 'high').length, color: '#EF4444' },
    { name: 'Medium', value: tasks.filter(t => t.priority === 'medium').length, color: '#F59E0B' },
    { name: 'Low', value: tasks.filter(t => t.priority === 'low').length, color: '#10B981' },
  ] // Don't filter out zero values as we need to show all priority levels in the chart

  const total = priorityData.reduce((sum, item) => sum + item.value, 0)

  // Define colors for each priority level
  const priorityColors: Record<string, string> = {
    'High': '#EF4444',
    'Medium': '#F59E0B',
    'Low': '#10B981',
  }

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

      {total === 0 ? (
        <div className="flex flex-col items-center justify-center h-[250px] text-center">
          <Clock className="h-12 w-12 text-gray-400 mb-4" />
          <h4 className="text-lg font-medium text-gray-500">No tasks</h4>
          <p className="text-sm text-gray-500 max-w-xs">
            Add tasks to see how they are distributed by priority
          </p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={250}>
          <PieChart>
            <Pie
              data={priorityData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
            >
              {priorityData.map((entry, index) => (
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
      )}
    </Card>
  )
}
