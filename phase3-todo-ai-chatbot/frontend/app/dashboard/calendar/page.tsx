'use client';

import { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock, Plus } from 'lucide-react';
import { useTasks } from '@/hooks/useTasks';
import { useUIStore } from '@/store/uiStore';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, addDays, isSameMonth, isSameDay, isToday, parseISO } from 'date-fns';

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const openCreateTaskModal = useUIStore((state) => state.openCreateTaskModal);
  const { tasks, loading, updateTask, deleteTask } = useTasks();

  // Get task dates with their data
  const tasksByDate = useMemo(() => {
    const map = new Map<string, typeof tasks>();
    tasks.forEach((task) => {
      if (task.due_date) {
        const dateKey = format(parseISO(task.due_date), 'yyyy-MM-dd');
        const existing = map.get(dateKey) || [];
        map.set(dateKey, [...existing, task]);
      }
    });
    return map;
  }, [tasks]);

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const monthStart = startOfMonth(currentDate);
    const monthEnd = endOfMonth(monthStart);
    const startDate = startOfWeek(monthStart);
    const endDate = endOfWeek(monthEnd);

    const days = [];
    let day = startDate;

    while (day <= endDate) {
      days.push(day);
      day = addDays(day, 1);
    }

    return days;
  }, [currentDate]);

  const goToPreviousMonth = () => {
    setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate((prev) => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-500/80 dark:bg-red-500/60';
      case 'high': return 'bg-orange-500/80 dark:bg-orange-500/60';
      case 'medium': return 'bg-yellow-500/80 dark:bg-yellow-500/60';
      default: return 'bg-green-500/80 dark:bg-green-500/60';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] bg-clip-text text-transparent flex items-center gap-3">
            <CalendarIcon size={32} className="text-[#6EB8E1]" />
            Calendar
          </h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-gray-600 dark:text-gray-400 mt-1"
          >
            View and manage tasks by due date
          </motion.p>
        </div>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={openCreateTaskModal}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all"
        >
          <Plus size={20} />
          New Task
        </motion.button>
      </div>

      {/* Calendar Navigation */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-4 rounded-2xl"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={goToPreviousMonth}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <ChevronLeft size={24} className="text-gray-600 dark:text-gray-400" />
            </motion.button>

            <h2 className="text-xl font-semibold text-gray-900 dark:text-white min-w-[180px] text-center">
              {format(currentDate, 'MMMM yyyy')}
            </h2>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={goToNextMonth}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <ChevronRight size={24} className="text-gray-600 dark:text-gray-400" />
            </motion.button>
          </div>

          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={goToToday}
            className="px-4 py-2 bg-[#6EB8E1]/10 text-[#6EB8E1] dark:text-[#4EB5A9] rounded-lg font-medium hover:bg-[#6EB8E1]/20 transition-colors"
          >
            Today
          </motion.button>
        </div>
      </motion.div>

      {/* Calendar Grid */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass-card rounded-2xl overflow-hidden"
      >
        {/* Day Headers */}
        <div className="grid grid-cols-7 border-b border-gray-200/50 dark:border-gray-700/50">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
            <div
              key={day}
              className="p-3 text-center text-sm font-medium text-gray-500 dark:text-gray-400 bg-gray-50/50 dark:bg-[#201761]/30"
            >
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7">
          {calendarDays.map((day, index) => {
            const dateKey = format(day, 'yyyy-MM-dd');
            const dayTasks = tasksByDate.get(dateKey) || [];
            const isCurrentMonth = isSameMonth(day, currentDate);
            const isDayToday = isToday(day);

            return (
              <div
                key={index}
                className={`
                  min-h-[120px] p-2 border-b border-r border-gray-200/50 dark:border-gray-700/50
                  ${!isCurrentMonth ? 'bg-gray-50/30 dark:bg-gray-900/20' : ''}
                  ${isDayToday ? 'bg-[#6EB8E1]/5 dark:bg-[#4EB5A9]/10' : ''}
                `}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className={`
                    w-7 h-7 flex items-center justify-center rounded-full text-sm font-medium
                    ${isDayToday
                      ? 'bg-gradient-to-br from-[#6EB8E1] to-[#4EB5A9] text-white shadow-lg'
                      : isCurrentMonth
                        ? 'text-gray-900 dark:text-white'
                        : 'text-gray-400 dark:text-gray-600'
                    }
                  `}>
                    {format(day, 'd')}
                  </span>

                  {dayTasks.length > 0 && (
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {dayTasks.length} {dayTasks.length === 1 ? 'task' : 'tasks'}
                    </span>
                  )}
                </div>

                {/* Task indicators */}
                <div className="space-y-1">
                  {dayTasks.slice(0, 3).map((task) => (
                    <motion.div
                      key={task.id}
                      whileHover={{ scale: 1.02 }}
                      className={`
                        px-2 py-1 rounded-lg text-xs font-medium truncate cursor-pointer
                        ${getPriorityColor(task.priority)}
                        text-white
                        ${task.status === 'completed' ? 'opacity-60 line-through' : ''}
                      `}
                      title={task.title}
                    >
                      {task.title}
                    </motion.div>
                  ))}
                  {dayTasks.length > 3 && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 pl-2">
                      +{dayTasks.length - 3} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="flex flex-wrap gap-4 justify-center"
      >
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Urgent</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500/80" />
          <span className="text-sm text-gray-600 dark:text-gray-400">High</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Medium</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500/80" />
          <span className="text-sm text-gray-600 dark:text-gray-400">Low</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
