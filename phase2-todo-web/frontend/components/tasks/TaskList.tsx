'use client';

import { motion, AnimatePresence } from 'framer-motion';
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
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="text-center py-12"
      >
        <div className="inline-block">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full"
          />
        </div>
        <p className="mt-4 text-gray-600 dark:text-gray-400 font-medium">
          Loading tasks...
        </p>
      </motion.div>
    );
  }

  if (tasks.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center py-16 glass-card rounded-2xl"
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          className="text-6xl mb-4"
        >
          📝
        </motion.div>
        <h3 className="text-xl font-semibold text-gray-700 dark:text-gray-300 mb-2">
          No tasks yet
        </h3>
        <p className="text-gray-500 dark:text-gray-400">
          Create your first task to get started!
        </p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onUpdate={onUpdate}
            onDelete={onDelete}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
