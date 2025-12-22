'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth';
import { useTasks } from '@/hooks/useTasks';
import { TaskForm } from '@/components/tasks/TaskForm';
import { TaskList } from '@/components/tasks/TaskList';

export default function TasksPage() {
  const { isAuthenticated, isLoading: authLoading, user, logout } = useAuth();
  const router = useRouter();
  const [statusFilter, setStatusFilter] = useState<string | undefined>(undefined);
  const { tasks, loading, createTask, updateTask, deleteTask } = useTasks(statusFilter);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/login');
    }
  }, [isAuthenticated, authLoading, router]);

  if (authLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-2xl font-bold">My Tasks</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {user?.name}
            </span>
            <button onClick={logout} className="btn-secondary text-sm">
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Task Form */}
          <div className="md:col-span-1">
            <div className="card sticky top-4">
              <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
              <TaskForm onSubmit={createTask} />
            </div>
          </div>

          {/* Task List */}
          <div className="md:col-span-2">
            {/* Filters */}
            <div className="flex gap-2 mb-6">
              <button
                onClick={() => setStatusFilter(undefined)}
                className={`px-4 py-2 rounded-lg ${
                  statusFilter === undefined
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setStatusFilter('pending')}
                className={`px-4 py-2 rounded-lg ${
                  statusFilter === 'pending'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                Pending
              </button>
              <button
                onClick={() => setStatusFilter('completed')}
                className={`px-4 py-2 rounded-lg ${
                  statusFilter === 'completed'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700'
                }`}
              >
                Completed
              </button>
            </div>

            <TaskList
              tasks={tasks}
              loading={loading}
              onUpdate={updateTask}
              onDelete={deleteTask}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
