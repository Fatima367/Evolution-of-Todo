'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Edit2, Trash2, Tag } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { Task } from '@/lib/types';
import { useUIStore } from '@/store/uiStore';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: string, data: any) => void;
  onDelete: (id: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  const { openEditTaskModal, openDeleteConfirmModal } = useUIStore();

  const toggleComplete = () => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    onUpdate(task.id, { status: newStatus });
  };

  // Priority-based neon border colors
  const priorityBorders = {
    low: 'border-green-400/50 hover:shadow-green-500/30',
    medium: 'border-yellow-400/50 hover:shadow-yellow-500/30',
    high: 'border-orange-400/50 hover:shadow-orange-500/30',
    urgent: 'border-red-400/50 hover:shadow-red-500/30',
  };

  // Priority badge colors
  const priorityColors = {
    low: 'bg-green-500/20 text-green-400 border-green-400/50',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/50',
    high: 'bg-orange-500/20 text-orange-400 border-orange-400/50',
    urgent: 'bg-red-500/20 text-red-400 border-red-400/50',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      whileHover={{ scale: 1.01 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={`
        glass-card rounded-2xl p-5
        border-2 ${priorityBorders[task.priority]}
        transition-all duration-300
        hover:shadow-2xl
        relative
      `}
    >
      {/* Priority Badge - Top Right Corner */}
      <div className="absolute top-4 right-4">
        <span
          className={`
            px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider
            border ${priorityColors[task.priority]}
          `}
        >
          {task.priority}
        </span>
      </div>

      <div className="flex items-start gap-4">
        {/* Left: Checkbox */}
        <motion.div
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          className="flex-shrink-0 mt-1"
        >
          <input
            type="checkbox"
            checked={task.status === 'completed'}
            onChange={toggleComplete}
            className="w-6 h-6 rounded-lg cursor-pointer accent-purple-500 transition-all"
          />
        </motion.div>

        {/* Center: Task Details */}
        <div className="flex-1 min-w-0 pr-12">
          {/* Title */}
          <h3
            className={`
              font-semibold text-lg mb-2
              ${
                task.status === 'completed'
                  ? 'line-through text-gray-500 dark:text-gray-500'
                  : 'text-gray-900 dark:text-white'
              }
            `}
          >
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Dates */}
          <div className="flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400 mb-3">
            <div className="flex items-center gap-1">
              <Calendar size={14} />
              <span>Created: {formatDate(task.created_at)}</span>
            </div>
            {task.due_date && (
              <div className="flex items-center gap-1">
                <Calendar size={14} />
                <span className="text-orange-500 dark:text-orange-400">
                  Due: {formatDate(task.due_date)}
                </span>
              </div>
            )}
          </div>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {task.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-purple-500/10 text-purple-400 rounded-lg text-xs font-medium border border-purple-400/30"
                >
                  <Tag size={12} />
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right: Edit/Delete Icons - Appear on Hover */}
        <motion.div
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: isHovered ? 1 : 0, x: isHovered ? 0 : 10 }}
          transition={{ duration: 0.2 }}
          className="flex flex-col gap-2 absolute top-14 right-4"
        >
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => openEditTaskModal(task.id)}
            className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-400/50 transition-all"
            aria-label="Edit task"
          >
            <Edit2 size={16} />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => openDeleteConfirmModal(task.id, task.title)}
            className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-400/50 transition-all"
            aria-label="Delete task"
          >
            <Trash2 size={16} />
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
}
