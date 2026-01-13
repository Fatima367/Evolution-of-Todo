import { format, formatDistanceToNow, isToday, isTomorrow, isYesterday, isPast } from 'date-fns'

export function formatDate(date: Date | string | null): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, 'MMM dd, yyyy')
}

export function formatDateTime(date: Date | string | null): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, 'MMM dd, yyyy HH:mm')
}

export function formatRelativeDate(date: Date | string | null): string {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date

  if (isToday(d)) return 'Today'
  if (isTomorrow(d)) return 'Tomorrow'
  if (isYesterday(d)) return 'Yesterday'

  return formatDistanceToNow(d, { addSuffix: true })
}

export function isDueSoon(dueDate: Date | string | null): boolean {
  if (!dueDate) return false
  const d = typeof dueDate === 'string' ? new Date(dueDate) : dueDate
  const now = new Date()
  const hoursDiff = (d.getTime() - now.getTime()) / (1000 * 60 * 60)
  return hoursDiff > 0 && hoursDiff <= 24
}

export function isOverdue(dueDate: Date | string | null): boolean {
  if (!dueDate) return false
  const d = typeof dueDate === 'string' ? new Date(dueDate) : dueDate
  return isPast(d) && !isToday(d)
}

export function getDueDateColor(dueDate: Date | string | null): string {
  if (!dueDate) return 'gray'
  if (isOverdue(dueDate)) return 'red'
  if (isDueSoon(dueDate)) return 'yellow'
  return 'gray'
}
