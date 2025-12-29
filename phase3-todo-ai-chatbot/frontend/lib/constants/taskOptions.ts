export const TASK_STATUSES = [
  { value: 'pending', label: 'Pending', color: 'gray' },
  { value: 'in_progress', label: 'In Progress', color: 'blue' },
  { value: 'completed', label: 'Completed', color: 'green' },
] as const

export const TASK_PRIORITIES = [
  { value: 'low', label: 'Low', color: 'green', glow: 'glow-green' },
  { value: 'medium', label: 'Medium', color: 'yellow', glow: 'glow-yellow' },
  { value: 'high', label: 'High', color: 'orange', glow: 'glow-orange' },
  { value: 'urgent', label: 'Urgent', color: 'red', glow: 'glow-red' },
] as const

export const COMMON_TAGS = [
  'work',
  'personal',
  'urgent',
  'meeting',
  'project',
  'bug',
  'feature',
  'documentation',
  'review',
  'research',
]

export const CHART_COLORS = {
  blue: '#3B82F6',
  purple: '#A855F7',
  green: '#10B981',
  yellow: '#F59E0B',
  red: '#EF4444',
  pink: '#EC4899',
  orange: '#F97316',
}
