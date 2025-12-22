'use client';

import { formatDate } from '@/lib/utils';
import type { Task } from '@/lib/types';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: string, data: any) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const toggleComplete = () => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    onUpdate(task.id, { status: newStatus });
  };

  const priorityColors = {
    low: 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400',
    medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400',
    high: 'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400',
    urgent: 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400',
  };

  return (
    <div className="card flex items-start gap-4">
      <input
        type="checkbox"
        checked={task.status === 'completed'}
        onChange={toggleComplete}
        className="mt-1 w-5 h-5 cursor-pointer"
      />
      <div className="flex-1">
        <h3
          className={`font-medium text-lg ${
            task.status === 'completed' ? 'line-through text-gray-500' : ''
          }`}
        >
          {task.title}
        </h3>
        {task.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {task.description}
          </p>
        )}
        <div className="flex gap-2 mt-2 flex-wrap">
          <span
            className={`text-xs px-2 py-1 rounded ${priorityColors[task.priority]}`}
          >
            {task.priority}
          </span>
          <span className="text-xs text-gray-500">
            Created {formatDate(task.created_at)}
          </span>
        </div>
      </div>
      <button
        onClick={() => onDelete(task.id)}
        className="text-red-600 hover:text-red-700 px-3 py-1 rounded hover:bg-red-50 dark:hover:bg-red-900/20"
      >
        Delete
      </button>
    </div>
  );
}
