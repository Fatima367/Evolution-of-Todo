'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import type { Task, TaskCreate, TaskUpdate, SortField, SortDirection } from '@/lib/types';

export function useTasks(
  statusFilter?: string,
  sortBy?: SortField,
  sortOrder?: SortDirection,
  isFavorite?: boolean | undefined
) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const params: {
        status?: string;
        sort_by?: SortField;
        sort_order?: SortDirection;
        is_favorite?: boolean | undefined;
      } = {
        status: statusFilter,
        sort_by: sortBy,
        sort_order: sortOrder,
      };
      // Only include is_favorite if explicitly set (not undefined)
      if (isFavorite !== undefined) {
        params.is_favorite = isFavorite;
      }

      const response = await apiClient.getTasks(params);
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load tasks'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refetch();
  }, [statusFilter, sortBy, sortOrder, isFavorite]);

  const createTask = async (data: TaskCreate) => {
    const newTask = await apiClient.createTask(data);
    setTasks([newTask, ...tasks]);
    return newTask;
  };

  const updateTask = async (id: string, data: TaskUpdate) => {
    const updated = await apiClient.updateTask(id, data);
    setTasks(tasks.map(t => t.id === id ? updated : t));
    return updated;
  };

  const toggleFavorite = async (id: string) => {
    const updated = await apiClient.toggleFavorite(id);
    setTasks(tasks.map(t => t.id === id ? updated : t));
    return updated;
  };

  const deleteTask = async (id: string) => {
    await apiClient.deleteTask(id);
    setTasks(tasks.filter(t => t.id !== id));
  };

  return {
    tasks,
    loading,
    error,
    refetch,
    createTask,
    updateTask,
    toggleFavorite,
    deleteTask,
  };
}
