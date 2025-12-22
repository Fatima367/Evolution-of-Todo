'use client';

import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { useTasks } from '@/hooks/useTasks';
import { useTaskFilters } from '@/lib/hooks/useTaskFilters';
import { useUIStore } from '@/store/uiStore';
import { TaskList } from '@/components/tasks/TaskList';

export default function TasksPage() {
  const openCreateTaskModal = useUIStore((state) => state.openCreateTaskModal);
  const { tasks, loading, updateTask, deleteTask } = useTasks();
  const { filteredTasks, filters, updateFilter, activeFilterCount } = useTaskFilters(tasks);

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
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            My Tasks
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
            {activeFilterCount > 0 && ` (${activeFilterCount} ${activeFilterCount === 1 ? 'filter' : 'filters'} active)`}
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={openCreateTaskModal}
          className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all glow-purple"
        >
          <Plus size={20} />
          New Task
        </motion.button>
      </div>

      {/* Search and Filters - Placeholder for now, will be enhanced */}
      <div className="glass-card p-6 rounded-2xl">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search Bar Placeholder */}
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search tasks..."
              value={filters.searchQuery || ''}
              onChange={(e) => updateFilter('searchQuery', e.target.value)}
              className="w-full px-4 py-3 bg-white/50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          {/* Filter Buttons Placeholder */}
          <div className="flex gap-2">
            <button className="px-4 py-3 glass-card rounded-xl hover:glow-purple transition-all">
              Status
            </button>
            <button className="px-4 py-3 glass-card rounded-xl hover:glow-purple transition-all">
              Priority
            </button>
            <button className="px-4 py-3 glass-card rounded-xl hover:glow-purple transition-all">
              Tags
            </button>
          </div>
        </div>
      </div>

      {/* Task List */}
      <TaskList
        tasks={filteredTasks}
        loading={loading}
        onUpdate={updateTask}
        onDelete={deleteTask}
      />
    </motion.div>
  );
}
