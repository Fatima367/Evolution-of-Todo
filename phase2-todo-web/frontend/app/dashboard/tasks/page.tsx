'use client';

import { motion } from 'framer-motion';
import { Plus, Filter, ListChecks } from 'lucide-react';
import { useTasks } from '@/hooks/useTasks';
import { useTaskFilters } from '@/lib/hooks/useTaskFilters';
import { useUIStore } from '@/store/uiStore';
import { TaskList } from '@/components/tasks/TaskList';
import { SearchBar } from '@/components/tasks/SearchBar';
import { FilterDropdown } from '@/components/tasks/FilterDropdown';
import { TASK_STATUSES, TASK_PRIORITIES } from '@/lib/constants/taskOptions';

export default function TasksPage() {
  const openCreateTaskModal = useUIStore((state) => state.openCreateTaskModal);
  const { tasks, loading, updateTask, deleteTask } = useTasks();
  const { filteredTasks, filters, updateFilter, activeFilterCount } = useTaskFilters(tasks);

  // Prepare filter options
  const statusOptions = TASK_STATUSES.map((status) => ({
    value: status.value,
    label: status.label,
  }));

  const priorityOptions = TASK_PRIORITIES.map((priority) => ({
    value: priority.value,
    label: priority.label,
  }));

  // Extract unique tags from all tasks
  const allTags = Array.from(
    new Set(
      tasks.flatMap((task) => task.tags || [])
    )
  ).map((tag) => ({
    value: tag,
    label: tag,
  }));

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
            <ListChecks size={32} className="text-[#6EB8E1]" />
            My Tasks
          </h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-gray-600 dark:text-gray-400 mt-1"
          >
            {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
            {activeFilterCount > 0 && (
              <span className="ml-2 text-[#5A7FC8]">
                ({activeFilterCount} {activeFilterCount === 1 ? 'filter' : 'filters'} active)
              </span>
            )}
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

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-6 rounded-2xl"
      >
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search Bar */}
          <SearchBar
            value={filters.searchQuery || ''}
            onChange={(value) => updateFilter('searchQuery', value)}
            placeholder="Search tasks by title or description..."
          />

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap gap-3">
            {/* Status Filter */}
            <FilterDropdown
              label="Status"
              options={statusOptions}
              selectedValues={filters.status || []}
              onChange={(values) => updateFilter('status', values)}
              icon={<Filter size={18} />}
            />

            {/* Priority Filter */}
            <FilterDropdown
              label="Priority"
              options={priorityOptions}
              selectedValues={filters.priority || []}
              onChange={(values) => updateFilter('priority', values)}
              icon={<Filter size={18} />}
            />

            {/* Tags Filter */}
            {allTags.length > 0 && (
              <FilterDropdown
                label="Tags"
                options={allTags}
                selectedValues={filters.tags || []}
                onChange={(values) => updateFilter('tags', values)}
                icon={<Filter size={18} />}
              />
            )}
          </div>
        </div>

        {/* Active Filters Summary */}
        {activeFilterCount > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 pt-4 border-t border-gray-200/50 dark:border-gray-700/50"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Showing {filteredTasks.length} of {tasks.length} tasks
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  updateFilter('searchQuery', '');
                  updateFilter('status', []);
                  updateFilter('priority', []);
                  updateFilter('tags', []);
                }}
                className="text-sm text-[#5A7FC8] hover:text-[#4EB5A9] font-medium"
              >
                Clear all filters
              </motion.button>
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Task Stats */}
      {!loading && tasks.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-3 gap-4"
        >
          <div className="glass-card p-4 rounded-xl bg-white/50 dark:bg-[#201761]/50">
            <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">Total</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-[#F7F6F7] mt-1">
              {tasks.length}
            </p>
          </div>
          <div className="glass-card p-4 rounded-xl bg-white/50 dark:bg-[#201761]/50">
            <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">Pending</p>
            <p className="text-2xl font-bold text-yellow-500 dark:text-yellow-400 mt-1">
              {tasks.filter((t) => t.status === 'pending').length}
            </p>
          </div>
          {/* <div className="glass-card p-4 rounded-xl bg-white/50 dark:bg-[#201761]/50">
            <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">In Progress</p>
            <p className="text-2xl font-bold text-blue-500 dark:text-blue-400 mt-1">
              {tasks.filter((t) => t.status === 'in_progress').length}
            </p>
          </div> */}
          <div className="glass-card p-4 rounded-xl bg-white/50 dark:bg-[#201761]/50">
            <p className="text-sm text-gray-500 dark:text-[#C8C8D8]">Completed</p>
            <p className="text-2xl font-bold text-green-500 dark:text-green-400 mt-1">
              {tasks.filter((t) => t.status === 'completed').length}
            </p>
          </div>
        </motion.div>
      )}

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
