'use client';

import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api';
import type { Task } from '@/lib/types';

interface DashboardStats {
  totalTasks: number;
  inProgressTasks: number;
  completedTasks: number;
  highPriorityTasks: number;
}

export function useDashboardStats() {
  const [stats, setStats] = useState<DashboardStats>({
    totalTasks: 0,
    inProgressTasks: 0,
    completedTasks: 0,
    highPriorityTasks: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const calculateStats = (tasks: Task[]) => {
    const totalTasks = tasks.length;
    const inProgressTasks = tasks.filter(task => !task.completed).length;
    const completedTasks = tasks.filter(task => task.completed).length;
    const highPriorityTasks = tasks.filter(task => task.priority === 'high').length;

    setStats({
      totalTasks,
      inProgressTasks,
      completedTasks,
      highPriorityTasks,
    });
  };

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.getTasks();
      calculateStats(response.tasks);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load dashboard stats'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  return {
    stats,
    loading,
    error,
    refreshStats: loadStats,
  };
}