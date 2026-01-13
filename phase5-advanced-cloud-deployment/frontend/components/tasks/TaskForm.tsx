'use client';

import { useState } from 'react';
import { Repeat, Calendar, Tag, X } from 'lucide-react';
import type { TaskCreate, TaskPriority, RecurringType } from '@/lib/types';

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>;
  onCancel?: () => void;
  initialData?: Partial<TaskCreate>;
}

export function TaskForm({ onSubmit, onCancel, initialData }: TaskFormProps) {
  const [title, setTitle] = useState(initialData?.title || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [priority, setPriority] = useState<TaskPriority>(initialData?.priority || 'medium');
  const [recurringType, setRecurringType] = useState<RecurringType>(initialData?.recurring_type || 'none');
  const [dueDate, setDueDate] = useState(initialData?.due_date || '');
  const [tags, setTags] = useState<string[]>(initialData?.tags || []);
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAddTag = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault();
      if (!tags.includes(tagInput.trim()) && tags.length < 10) {
        setTags([...tags, tagInput.trim()]);
        setTagInput('');
      }
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter(tag => tag !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await onSubmit({
        title,
        description: description || undefined,
        priority,
        recurring_type: recurringType,
        due_date: dueDate || undefined,
        tags: tags.length > 0 ? tags : undefined,
      });
      setTitle('');
      setDescription('');
      setPriority('medium');
      setRecurringType('none');
      setDueDate('');
      setTags([]);
      setTagInput('');
    } catch (error) {
      console.error('Failed to create task:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] placeholder:text-gray-400 dark:placeholder:text-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
          placeholder="What needs to be done?"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={10000}
          rows={3}
          className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] placeholder:text-gray-400 dark:placeholder:text-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all resize-none"
          placeholder="Add more details..."
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="priority" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value as TaskPriority)}
            className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>

        <div>
          <label htmlFor="recurring" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300 flex items-center gap-1">
            <Repeat size={14} className="text-purple-400" />
            Recurring
          </label>
          <select
            id="recurring"
            value={recurringType}
            onChange={(e) => setRecurringType(e.target.value as RecurringType)}
            className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
          >
            <option value="none">One-time</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
      </div>

      <div>
        <label htmlFor="dueDate" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300 flex items-center gap-1">
          <Calendar size={14} className="text-blue-400" />
          Due Date
        </label>
        <input
          id="dueDate"
          type="datetime-local"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
        />
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300 flex items-center gap-1">
          <Tag size={14} className="text-green-400" />
          Tags (Press Enter to add)
        </label>
        <input
          id="tags"
          type="text"
          value={tagInput}
          onChange={(e) => setTagInput(e.target.value)}
          onKeyDown={handleAddTag}
          maxLength={50}
          placeholder="Add tags..."
          className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] placeholder:text-gray-400 dark:placeholder:text-gray-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
        />
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r from-[#6EB8E1]/20 to-[#5A7FC8]/20 dark:from-[#C8ABE6]/20 dark:to-[#48ADB7]/20 text-[#5A7FC8] dark:text-[#C8ABE6] rounded-full text-sm border border-[#6EB8E1]/30 dark:border-[#C8ABE6]/30"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => handleRemoveTag(tag)}
                  className="hover:text-red-500 transition-colors"
                >
                  <X size={14} />
                </button>
              </span>
            ))}
          </div>
        )}
        {tags.length >= 10 && (
          <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
            Maximum 10 tags allowed
          </p>
        )}
      </div>

      <div className="flex gap-2">
        <button type="submit" disabled={loading || !title} className="flex-1 px-4 py-2 bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white rounded-lg shadow-lg shadow-[#6EB8E1]/30 hover:shadow-xl hover:from-[#5A7FC8] hover:to-[#252E8A] transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95">
          {loading ? 'Creating...' : 'Create Task'}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} className="px-4 py-2 bg-gradient-to-br from-[#D6E6F2] to-[#BAD0CC] dark:from-[#252E8A]/50 dark:to-[#5A7FC8]/30 text-[#5A7FC8] dark:text-[#6EB8E1] border-2 border-[#6EB8E1] dark:border-[#5A7FC8] rounded-lg shadow-md hover:shadow-lg transition-all active:scale-95">
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
