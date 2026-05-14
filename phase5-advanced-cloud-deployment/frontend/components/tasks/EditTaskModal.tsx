'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, Tag as TagIcon, AlertCircle } from 'lucide-react';
import { useUIStore } from '@/store/uiStore';
import { useTasks } from '@/hooks/useTasks';
import type { TaskPriority, Task, RecurringType } from '@/lib/types';

const priorityOptions: { value: TaskPriority; label: string; color: string }[] = [
  { value: 'low', label: 'Low', color: 'bg-green-500' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-500' },
  { value: 'high', label: 'High', color: 'bg-orange-500' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-500' },
];

export function EditTaskModal() {
  const { isEditTaskModalOpen, closeEditTaskModal, editingTaskId } = useUIStore();
  const { tasks, updateTask, loading } = useTasks();
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<TaskPriority>('medium');
  const [dueDate, setDueDate] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [recurringType, setRecurringType] = useState<RecurringType>('none');
  const [interval, setInterval] = useState(1);
  const [dayOfWeek, setDayOfWeek] = useState(0);
  const [dayOfMonth, setDayOfMonth] = useState(1);
  const [monthOfYear, setMonthOfYear] = useState(1);
  const [endDate, setEndDate] = useState('');
  const [reminderOffset, setReminderOffset] = useState(15);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleClose = () => {
    closeEditTaskModal();
    // Reset form after animation completes
    setTimeout(() => {
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
      setTags([]);
      setTagInput('');
      setRecurringType('none');
      setInterval(1);
      setDayOfWeek(0);
      setDayOfMonth(1);
      setMonthOfYear(1);
      setEndDate('');
      setReminderOffset(15);
      setErrors({});
    }, 300);
  };

  // Find task to edit when modal opens or editingTaskId changes
  useEffect(() => {
    if (editingTaskId) {
      const task = tasks.find(t => t.id === editingTaskId);
      if (task) {
        setTaskToEdit(task);
        setTitle(task.title);
        setDescription(task.description || '');
        setPriority(task.priority as TaskPriority);
        setDueDate(task.due_date || '');
        setTags(task.tags || []);
        setRecurringType(task.recurring_type || 'none');
        setInterval(task.interval || 1);
        setDayOfWeek(task.day_of_week || 0);
        setDayOfMonth(task.day_of_month || 1);
        setMonthOfYear(task.month_of_year || 1);
        setEndDate(task.end_date || '');
        setReminderOffset(task.reminder_offset ?? 15);
      } else if (!loading && tasks.length > 0) {
        handleClose();
      }
    }
  }, [editingTaskId, tasks, loading]);

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim())) {
        setTags([...tags, tagInput.trim()]);
      }
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  const validateForm = () => {
    const newErrors: { [key: string]: string } = {};

    if (!title.trim()) {
      newErrors.title = 'Title is required';
    } else if (title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters';
    }

    if (dueDate) {
      const dueDateObj = new Date(dueDate);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (dueDateObj < today) {
        newErrors.dueDate = 'Due date cannot be in the past';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      if (taskToEdit) {
        await updateTask(taskToEdit.id, {
          title: title.trim(),
          description: description.trim() || undefined,
          priority,
          due_date: dueDate || undefined,
          reminder_offset: reminderOffset,
          tags: tags.length > 0 ? tags : undefined,
          recurring_type: recurringType,
          ...(recurringType !== 'none' && {
              interval: interval,
              day_of_week: recurringType === 'weekly' ? dayOfWeek : undefined,
              day_of_month: recurringType === 'monthly' ? dayOfMonth : undefined,
              month_of_year: recurringType === 'yearly' ? monthOfYear : undefined,
              end_date: endDate || undefined,
          }),
        });
      }
      handleClose();
    } catch (error) {
      setErrors({ submit: 'Failed to update task. Please try again.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Close modal when task is deleted
  useEffect(() => {
    if (taskToEdit && !tasks.some(t => t.id === taskToEdit.id)) {
      handleClose();
    }
  }, [tasks, taskToEdit]);

  return (
    <AnimatePresence>
      {isEditTaskModalOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={handleClose}
          className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl max-h-[90vh] glass-card rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200/50 dark:border-gray-700/50 flex-shrink-0">
              <h2 className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-[#163cb7] to-[#149c8c] dark:from-[#6EB8E1] dark:to-[#4EB5A9] bg-clip-text text-transparent">
                Edit Task
              </h2>
              <motion.button
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleClose}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Close modal"
              >
                <X size={24} className="text-gray-500 dark:text-gray-400" />
              </motion.button>
            </div>

            {/* Form - Scrollable content */}
            <div className="flex-1 overflow-y-auto">
              <form onSubmit={handleSubmit} className="p-4 sm:p-6 space-y-4 sm:space-y-5">
              {/* Title */}
              <div>
                <label htmlFor="title" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  id="title"
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Enter task title..."
                  className={`
                    w-full px-4 py-3 glass-card rounded-xl
                    border-2 ${errors.title ? 'border-red-500' : 'border-gray-200/50 dark:border-gray-700/50'}
                    focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50
                    text-gray-900 dark:text-white placeholder:text-gray-500
                  `}
                />
                {errors.title && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-1 text-sm text-red-500 flex items-center gap-1"
                  >
                    <AlertCircle size={14} />
                    {errors.title}
                  </motion.p>
                )}
              </div>

              {/* Description */}
              <div>
                <label htmlFor="description" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add a description (optional)..."
                  rows={3}
                  className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white placeholder:text-gray-500 resize-none"
                />
              </div>

              {/* Priority & Due Date */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Priority */}
                <div>
                  <label htmlFor="priority" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Priority
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {priorityOptions.map((option) => (
                      <motion.button
                        key={option.value}
                        type="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setPriority(option.value)}
                        className={`
                          px-4 py-2.5 rounded-xl font-medium transition-all
                          ${
                            priority === option.value
                              ? `${option.color} text-white shadow-lg`
                              : 'glass-card border-2 border-gray-200/50 dark:border-gray-700/50 text-gray-700 dark:text-gray-300'
                          }
                        `}
                      >
                        {option.label}
                      </motion.button>
                    ))}
                  </div>
                </div>

                {/* Due Date */}
                <div>
                  <label htmlFor="dueDate" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Due Date
                  </label>
                  <div className="relative">
                    <Calendar
                      size={18}
                      className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 pointer-events-none"
                    />
                    <input
                      id="dueDate"
                      type="date"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className={`
                        w-full pl-10 pr-4 py-3 glass-card rounded-xl
                        border-2 ${errors.dueDate ? 'border-red-500' : 'border-gray-200/50 dark:border-gray-700/50'}
                        focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50
                        text-gray-900 dark:text-white
                      `}
                    />
                  </div>
                  {errors.dueDate && (
                    <motion.p
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-1 text-sm text-red-500 flex items-center gap-1"
                    >
                      <AlertCircle size={14} />
                      {errors.dueDate}
                    </motion.p>
                  )}
                </div>
              </div>

              {/* Reminder Offset (Only if Due Date is set) */}
              {dueDate && (
                <div>
                  <label htmlFor="reminderOffset" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Reminder (minutes before due date)
                  </label>
                  <input
                    id="reminderOffset"
                    type="number"
                    value={reminderOffset}
                    onChange={(e) => setReminderOffset(parseInt(e.target.value))}
                    min={0}
                    max={1440}
                    className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                  />
                </div>
              )}

              {/* Recurring Type and Details */}
              <div className="space-y-4">
                {/* Recurring Type Select */}
                <div>
                  <label htmlFor="recurringType" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Recurring Type
                  </label>
                  <select
                    id="recurringType"
                    value={recurringType}
                    onChange={(e) => setRecurringType(e.target.value as RecurringType)}
                    className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                  >
                    <option value="none">None</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>

                {recurringType !== 'none' && (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {/* Interval */}
                      <div>
                        <label htmlFor="interval" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                          Repeat Every (Days/Weeks/Months/Years)
                        </label>
                        <input
                          id="interval"
                          type="number"
                          value={interval}
                          onChange={(e) => setInterval(parseInt(e.target.value))}
                          min={1}
                          className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                        />
                      </div>

                      {/* Day of Week (for Weekly) */}
                      {recurringType === 'weekly' && (
                        <div>
                          <label htmlFor="dayOfWeek" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Day of Week
                          </label>
                          <select
                            id="dayOfWeek"
                            value={dayOfWeek}
                            onChange={(e) => setDayOfWeek(parseInt(e.target.value))}
                            className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                          >
                            <option value={0}>Sunday</option>
                            <option value={1}>Monday</option>
                            <option value={2}>Tuesday</option>
                            <option value={3}>Wednesday</option>
                            <option value={4}>Thursday</option>
                            <option value={5}>Friday</option>
                            <option value={6}>Saturday</option>
                          </select>
                        </div>
                      )}

                      {/* Day of Month (for Monthly) */}
                      {recurringType === 'monthly' && (
                        <div>
                          <label htmlFor="dayOfMonth" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Day of Month
                          </label>
                          <input
                            id="dayOfMonth"
                            type="number"
                            value={dayOfMonth}
                            onChange={(e) => setDayOfMonth(parseInt(e.target.value))}
                            min={1}
                            max={31}
                            className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                          />
                        </div>
                      )}

                      {/* Month of Year (for Yearly) */}
                      {recurringType === 'yearly' && (
                        <div>
                          <label htmlFor="monthOfYear" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                            Month of Year
                          </label>
                          <input
                            id="monthOfYear"
                            type="number"
                            value={monthOfYear}
                            onChange={(e) => setMonthOfYear(parseInt(e.target.value))}
                            min={1}
                            max={12}
                            className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                          />
                        </div>
                      )}
                    </div>

                    {/* End Date (for all recurring types except 'none') */}
                    <div>
                      <label htmlFor="endDate" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                        End Date (Optional)
                      </label>
                      <input
                        id="endDate"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="w-full px-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white"
                      />
                    </div>
                  </>
                )}
              </div>

              {/* Tags */}
              <div>
                <label htmlFor="tags" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Tags
                </label>
                <div className="relative">
                  <TagIcon
                    size={18}
                    className="absolute left-3 top-3 text-gray-500 pointer-events-none"
                  />
                  <input
                    id="tags"
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={handleAddTag}
                    placeholder="Type and press Enter to add tags..."
                    className="w-full pl-10 pr-4 py-3 glass-card rounded-xl border-2 border-gray-200/50 dark:border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/50 text-gray-900 dark:text-white placeholder:text-gray-500"
                  />
                </div>
                {tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-3">
                    {tags.map((tag) => (
                      <motion.span
                        key={tag}
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        exit={{ scale: 0 }}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] text-white rounded-lg text-sm font-medium border border-[#4EB5A9]"
                      >
                        {tag}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-1 hover:text-[#d6f9f5] font-bold"
                        >
                          <X size={14} />
                        </button>
                      </motion.span>
                    ))}
                  </div>
                )}
              </div>

              {/* Error Message */}
              {errors.submit && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 bg-red-500/10 border border-red-500/50 rounded-xl text-red-500 text-sm flex items-center gap-2"
                >
                  <AlertCircle size={16} />
                  {errors.submit}
                </motion.div>
              )}

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleClose}
                  className="flex-1 px-6 py-3 glass-card rounded-xl font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                >
                  Cancel
                </motion.button>
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  disabled={isSubmitting}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? 'Updating...' : 'Update Task'}
                </motion.button>
              </div>
            </form>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
