import { useState, useEffect, useMemo } from 'react';
import { SortOption, SortField, SortDirection, SortConfig } from '../types';

const STORAGE_KEY = 'task_sort_preference';

// Default sort configurations for UI
const SORT_CONFIGS: SortConfig[] = [
  {
    label: 'Due Date',
    value: 'due_date',
    icon: 'Calendar',
    defaultDirection: 'asc' as SortDirection
  },
  {
    label: 'Priority',
    value: 'priority',
    icon: 'AlertCircle',
    defaultDirection: 'desc' as SortDirection
  },
  {
    label: 'Alphabetical',
    value: 'title',
    icon: 'Type',
    defaultDirection: 'asc' as SortDirection
  }
];

/**
 * Load sort preference from localStorage
 */
function loadSortPreference(): SortOption {
  if (typeof window === 'undefined') {
    return { field: 'created_at', direction: 'desc' };
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      // Validate stored preference
      if (parsed.field && parsed.direction) {
        return parsed as SortOption;
      }
    }
  } catch (error) {
    console.warn('Failed to load sort preference:', error);
  }

  // Default to created_at descending (newest first)
  return { field: 'created_at', direction: 'desc' };
}

/**
 * Save sort preference to localStorage
 */
function saveSortPreference(sort: SortOption): void {
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sort));
    } catch (error) {
      console.warn('Failed to save sort preference:', error);
    }
  }
}

/**
 * Custom hook for managing task sorting with localStorage persistence
 *
 * @returns Sort state and methods to update it
 */
export function useTaskSort() {
  const [sort, setSortState] = useState<SortOption>(loadSortPreference);

  // Persist sort changes to localStorage
  useEffect(() => {
    saveSortPreference(sort);
  }, [sort]);

  /**
   * Set the sort field and use its default direction
   */
  const setSortBy = (field: SortField) => {
    const config = SORT_CONFIGS.find(c => c.value === field);
    setSortState({
      field,
      direction: config?.defaultDirection || 'desc'
    });
  };

  /**
   * Toggle sort direction (asc <-> desc)
   */
  const toggleDirection = () => {
    setSortState(prev => ({
      field: prev.field,
      direction: prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  /**
   * Set both field and direction explicitly
   */
  const setSort = (field: SortField, direction: SortDirection) => {
    setSortState({ field, direction });
  };

  /**
   * Reset sort to default
   */
  const resetSort = () => {
    setSortState({ field: 'created_at', direction: 'desc' });
  };

  /**
   * Set sort - main entry point for SortDropdown component
   */
  const onChange = (newSort: SortOption) => {
    setSortState(newSort);
  };

  // Computed: Get sort label for UI display
  const sortLabel = useMemo(() => {
    const config = SORT_CONFIGS.find(c => c.value === sort.field);
    if (!config) {
      return sort.field;
    }

    const directionLabel = sort.direction === 'asc' ? 'Ascending' : 'Descending';
    return `${config.label} (${directionLabel})`;
  }, [sort]);

  // Computed: Get sort icon name
  const sortIcon = useMemo(() => {
    const config = SORT_CONFIGS.find(c => c.value === sort.field);
    return config?.icon || 'ArrowUpDown';
  }, [sort]);

  return {
    // State
    sort,
    sortLabel,
    sortIcon,

    // Methods
    onChange,
    setSortBy,
    toggleDirection,
    setSort,
    resetSort,

    // Configuration
    sortConfigs: SORT_CONFIGS
  };
}
