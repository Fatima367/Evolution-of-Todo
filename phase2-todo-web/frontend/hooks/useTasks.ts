'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import type { Task, TaskCreate, TaskUpdate } from '@/lib/types';

export function useTasks(statusFilter?: string) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getTasks({ status: statusFilter });
      setTasks(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load tasks'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, [statusFilter]);

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

  const deleteTask = async (id: string) => {
    await apiClient.deleteTask(id);
    setTasks(tasks.filter(t => t.id !== id));
  };

  return {
    tasks,
    loading,
    error,
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
  };
}
