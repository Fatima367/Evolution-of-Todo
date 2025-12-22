'use client';

import { TaskItem } from './TaskItem';
import type { Task } from '@/lib/types';

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onUpdate: (id: string, data: any) => void;
  onDelete: (id: string) => void;
}

export function TaskList({ tasks, loading, onUpdate, onDelete }: TaskListProps) {
  if (loading) {
    return <div className="text-center py-8">Loading tasks...</div>;
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No tasks yet. Create your first task to get started!
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
