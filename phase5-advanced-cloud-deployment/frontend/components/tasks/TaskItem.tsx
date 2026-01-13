'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Calendar, Edit2, Trash2, Tag, Star, Repeat } from 'lucide-react';
import { formatDate } from '@/lib/utils';
import type { Task } from '@/lib/types';
import { useUIStore } from '@/store/uiStore';

interface TaskItemProps {
  task: Task;
  onUpdate: (id: string, data: any) => void;
  onDelete: (id: string) => void;
  onToggleFavorite?: (id: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete, onToggleFavorite }: TaskItemProps) {
  const [isHovered, setIsHovered] = useState(false);
  const { openEditTaskModal, openDeleteConfirmModal } = useUIStore();

  const toggleComplete = () => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    onUpdate(task.id, { status: newStatus });
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onToggleFavorite) {
      onToggleFavorite(task.id);
    } else {
      onUpdate(task.id, { is_favorite: !task.is_favorite });
    }
  };

  // Priority-based neon border colors
  const priorityBorders = {
    low: 'border-green-400/50 dark:border-green-400/30 hover:shadow-green-500/30 dark:hover:shadow-green-500/20',
    medium: 'border-yellow-400/50 dark:border-yellow-400/30 hover:shadow-yellow-500/30 dark:hover:shadow-yellow-500/20',
    high: 'border-orange-400/50 dark:border-orange-400/30 hover:shadow-orange-500/30 dark:hover:shadow-orange-500/20',
    urgent: 'border-red-400/50 dark:border-red-400/30 hover:shadow-red-500/30 dark:hover:shadow-red-500/20',
  };

  // Priority badge colors
  const priorityColors = {
    low: 'bg-green-500/20 text-green-400 border-green-400/50 dark:bg-green-500/30 dark:text-green-300 dark:border-green-400/30',
    medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-400/50 dark:bg-yellow-500/30 dark:text-yellow-300 dark:border-yellow-400/30',
    high: 'bg-orange-500/20 text-orange-400 border-orange-400/50 dark:bg-orange-500/30 dark:text-orange-300 dark:border-orange-400/30',
    urgent: 'bg-red-500/20 text-red-400 border-red-400/50 dark:bg-red-500/30 dark:text-red-300 dark:border-red-400/30',
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
        bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl
        border-2 ${priorityBorders[task.priority]}
        transition-all duration-300
        hover:shadow-2xl
        relative
      `}
    >
      {/* Top Row: Priority Badge with Star on its left */}
      <div className="absolute top-4 right-4 flex items-center gap-2">
        {/* Favorite Button - immediately left of priority */}
        <motion.button
          whileHover={{ scale: 1.2, rotate: 15 }}
          whileTap={{ scale: 0.9 }}
          onClick={handleToggleFavorite}
          className={`
            p-1.5 rounded-lg transition-all
            ${task.is_favorite
              ? 'bg-yellow-500/20 text-yellow-400'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500 hover:bg-gray-200 dark:hover:bg-gray-700'
            }
          `}
          aria-label={task.is_favorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          <Star size={18} className={task.is_favorite ? 'fill-yellow-400' : ''} />
        </motion.button>

        <span
          className={`
            px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider
            border ${priorityColors[task.priority]}
          `}
        >
          {task.priority}
        </span>
      </div>

      <div className="flex items-start gap-4 pt-2">
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
            className="w-6 h-6 rounded-lg cursor-pointer accent-blue-500 transition-all"
          />
        </motion.div>

        {/* Center: Task Details */}
        <div className="flex-1 min-w-0">
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

          {/* Meta Info Row */}
          <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400 mb-3">
            <div className="flex items-center gap-1">
              <Calendar size={14} className="text-gray-400 align-middle" />
              <span className="align-middle leading-none">Created: {formatDate(task.created_at)}</span>
            </div>
            {task.due_date && (
              <div className="flex items-center gap-1">
                <Calendar size={14} className="text-orange-400 align-middle" />
                <span className="text-orange-500 dark:text-orange-400 align-middle leading-none">Due: {formatDate(task.due_date)}</span>
              </div>
            )}
            {task.recurring_type && task.recurring_type !== 'none' && (
              <div className="flex items-center gap-1">
                <Repeat size={14} className="text-blue-400 align-middle" />
                <span className="text-blue-400 capitalize align-middle leading-none">{task.recurring_type}</span>
              </div>
            )}
          </div>

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {task.tags.map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-500/10 text-blue-400 rounded-lg text-xs font-medium border border-blue-400/30 dark:bg-blue-500/20 dark:text-blue-300 dark:blue-blue-400/40"
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
          className="flex flex-col gap-2"
        >
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => openEditTaskModal(task.id)}
            className="p-2 rounded-lg bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 border border-blue-400/50 dark:bg-blue-500/30 dark:text-blue-300 dark:border-blue-400/40 transition-all"
            aria-label="Edit task"
          >
            <Edit2 size={16} />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => openDeleteConfirmModal(task.id, task.title)}
            className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-400/50 dark:bg-red-500/30 dark:text-red-300 dark:border-red-400/40 transition-all"
            aria-label="Delete task"
          >
            <Trash2 size={16} />
          </motion.button>
        </motion.div>
      </div>
    </motion.div>
  );
}
