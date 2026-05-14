import { useState, useMemo } from 'react'
import { Task } from '../types'

interface FilterOptions {
  status?: string[]
  priority?: string[]
  tags?: string[]
  searchQuery?: string
}

export function useTaskFilters(tasks: Task[]) {
  const [filters, setFilters] = useState<FilterOptions>({
    status: [],
    priority: [],
    tags: [],
    searchQuery: '',
  })

  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      // Search filter
      if (filters.searchQuery) {
        const query = filters.searchQuery.toLowerCase()
        const matchesSearch =
          task.title.toLowerCase().includes(query) ||
          task.description?.toLowerCase().includes(query)
        if (!matchesSearch) return false
      }

      // Status filter
      if (filters.status && filters.status.length > 0) {
        if (!filters.status.includes(task.status)) return false
      }

      // Priority filter
      if (filters.priority && filters.priority.length > 0) {
        if (!filters.priority.includes(task.priority)) return false
      }

      // Tags filter
      if (filters.tags && filters.tags.length > 0) {
        const taskTags = task.tags || []
        const hasMatchingTag = filters.tags.some((filterTag) =>
          taskTags.includes(filterTag)
        )
        if (!hasMatchingTag) return false
      }

      return true
    })
  }, [tasks, filters])

  const updateFilter = (key: keyof FilterOptions, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const clearFilters = () => {
    setFilters({
      status: [],
      priority: [],
      tags: [],
      searchQuery: '',
    })
  }

  const activeFilterCount = useMemo(() => {
    let count = 0
    if (filters.status && filters.status.length > 0) count++
    if (filters.priority && filters.priority.length > 0) count++
    if (filters.tags && filters.tags.length > 0) count++
    if (filters.searchQuery) count++
    return count
  }, [filters])

  return {
    filters,
    filteredTasks,
    updateFilter,
    clearFilters,
    activeFilterCount,
  }
}
