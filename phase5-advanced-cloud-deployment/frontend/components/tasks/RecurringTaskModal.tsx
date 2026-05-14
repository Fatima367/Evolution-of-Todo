'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Repeat, Calendar, AlertCircle } from 'lucide-react';

interface RecurringPattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom';
  interval: number;
  day_of_week?: number;
  day_of_month?: number;
  month_of_year?: number;
  end_date?: string;
}

interface RecurringTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (pattern: RecurringPattern) => Promise<void>;
  initialPattern?: RecurringPattern;
  taskTitle?: string;
}

const DAYS_OF_WEEK = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

const MONTHS = [
  { value: 1, label: 'January' },
  { value: 2, label: 'February' },
  { value: 3, label: 'March' },
  { value: 4, label: 'April' },
  { value: 5, label: 'May' },
  { value: 6, label: 'June' },
  { value: 7, label: 'July' },
  { value: 8, label: 'August' },
  { value: 9, label: 'September' },
  { value: 10, label: 'October' },
  { value: 11, label: 'November' },
  { value: 12, label: 'December' },
];

export function RecurringTaskModal({
  isOpen,
  onClose,
  onSave,
  initialPattern,
  taskTitle,
}: RecurringTaskModalProps) {
  const [frequency, setFrequency] = useState<RecurringPattern['frequency']>(
    initialPattern?.frequency || 'daily'
  );
  const [interval, setInterval] = useState(initialPattern?.interval || 1);
  const [dayOfWeek, setDayOfWeek] = useState<number | undefined>(initialPattern?.day_of_week);
  const [dayOfMonth, setDayOfMonth] = useState<number | undefined>(initialPattern?.day_of_month);
  const [monthOfYear, setMonthOfYear] = useState<number | undefined>(initialPattern?.month_of_year);
  const [endDate, setEndDate] = useState(initialPattern?.end_date || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (isOpen) {
      setFrequency(initialPattern?.frequency || 'daily');
      setInterval(initialPattern?.interval || 1);
      setDayOfWeek(initialPattern?.day_of_week);
      setDayOfMonth(initialPattern?.day_of_month);
      setMonthOfYear(initialPattern?.month_of_year);
      setEndDate(initialPattern?.end_date || '');
      setError(null);
    }
  }, [isOpen, initialPattern]);

  const validatePattern = (): string | null => {
    if (interval < 1) {
      return 'Interval must be at least 1';
    }

    if (frequency === 'weekly' && dayOfWeek === undefined) {
      return 'Please select a day of the week';
    }

    if (frequency === 'monthly' && (dayOfMonth === undefined || dayOfMonth < 1 || dayOfMonth > 31)) {
      return 'Please select a valid day of the month (1-31)';
    }

    if (frequency === 'yearly') {
      if (monthOfYear === undefined || monthOfYear < 1 || monthOfYear > 12) {
        return 'Please select a valid month';
      }
      if (dayOfMonth === undefined || dayOfMonth < 1 || dayOfMonth > 31) {
        return 'Please select a valid day of the month (1-31)';
      }
    }

    return null;
  };

  const handleSave = async () => {
    const validationError = validatePattern();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const pattern: RecurringPattern = {
        frequency,
        interval,
        ...(frequency === 'weekly' && { day_of_week: dayOfWeek }),
        ...(frequency === 'monthly' && { day_of_month: dayOfMonth }),
        ...(frequency === 'yearly' && {
          day_of_month: dayOfMonth,
          month_of_year: monthOfYear,
        }),
        ...(endDate && { end_date: endDate }),
      };

      await onSave(pattern);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save recurring pattern');
    } finally {
      setLoading(false);
    }
  };

  const getFrequencyLabel = () => {
    switch (frequency) {
      case 'daily':
        return interval === 1 ? 'Every day' : `Every ${interval} days`;
      case 'weekly':
        return interval === 1 ? 'Every week' : `Every ${interval} weeks`;
      case 'monthly':
        return interval === 1 ? 'Every month' : `Every ${interval} months`;
      case 'yearly':
        return interval === 1 ? 'Every year' : `Every ${interval} years`;
      default:
        return 'Custom';
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        />

        {/* Modal */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-2xl max-h-[90vh] overflow-y-auto glass-card rounded-2xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50"
        >
          {/* Header */}
          <div className="sticky top-0 z-10 flex items-center justify-between p-6 border-b border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-[#201761]/80 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-r from-[#6EB8E1]/20 to-[#5A7FC8]/20">
                <Repeat className="w-5 h-5 text-[#5A7FC8] dark:text-[#C8ABE6]" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  Recurring Pattern
                </h2>
                {taskTitle && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    for "{taskTitle}"
                  </p>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
              >
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
              </motion.div>
            )}

            {/* Frequency Selection */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                Repeat Frequency
              </label>
              <select
                value={frequency}
                onChange={(e) => setFrequency(e.target.value as RecurringPattern['frequency'])}
                className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>

            {/* Interval */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                Repeat Every
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="number"
                  min="1"
                  max="365"
                  value={interval}
                  onChange={(e) => setInterval(parseInt(e.target.value) || 1)}
                  className="w-24 px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
                />
                <span className="text-gray-600 dark:text-gray-400">
                  {frequency === 'daily' && 'day(s)'}
                  {frequency === 'weekly' && 'week(s)'}
                  {frequency === 'monthly' && 'month(s)'}
                  {frequency === 'yearly' && 'year(s)'}
                </span>
              </div>
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                {getFrequencyLabel()}
              </p>
            </div>

            {/* Day of Week (for weekly) */}
            {frequency === 'weekly' && (
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                  On Day
                </label>
                <select
                  value={dayOfWeek ?? ''}
                  onChange={(e) => setDayOfWeek(parseInt(e.target.value))}
                  className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
                >
                  <option value="">Select a day</option>
                  {DAYS_OF_WEEK.map((day) => (
                    <option key={day.value} value={day.value}>
                      {day.label}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Day of Month (for monthly) */}
            {frequency === 'monthly' && (
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                  On Day of Month
                </label>
                <input
                  type="number"
                  min="1"
                  max="31"
                  value={dayOfMonth ?? ''}
                  onChange={(e) => setDayOfMonth(parseInt(e.target.value) || undefined)}
                  placeholder="1-31"
                  className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Note: If the day doesn't exist in a month (e.g., Feb 31), the last day of that month will be used.
                </p>
              </div>
            )}

            {/* Month and Day (for yearly) */}
            {frequency === 'yearly' && (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    Month
                  </label>
                  <select
                    value={monthOfYear ?? ''}
                    onChange={(e) => setMonthOfYear(parseInt(e.target.value))}
                    className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
                  >
                    <option value="">Select month</option>
                    {MONTHS.map((month) => (
                      <option key={month.value} value={month.value}>
                        {month.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                    Day
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={dayOfMonth ?? ''}
                    onChange={(e) => setDayOfMonth(parseInt(e.target.value) || undefined)}
                    placeholder="1-31"
                    className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
                  />
                </div>
              </div>
            )}

            {/* End Date */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-400" />
                End Date (Optional)
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2.5 border border-[#BAD0CC] dark:border-[#5A7FC8]/50 bg-white dark:bg-[#201761]/30 text-[#201761] dark:text-[#F7F6F7] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#6EB8E1]/20 transition-all"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Leave empty to repeat indefinitely
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="sticky bottom-0 flex items-center justify-end gap-3 p-6 border-t border-gray-200/50 dark:border-gray-700/50 bg-white/80 dark:bg-[#201761]/80 backdrop-blur-sm">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2.5 bg-gradient-to-br from-[#D6E6F2] to-[#BAD0CC] dark:from-[#252E8A]/50 dark:to-[#5A7FC8]/30 text-[#5A7FC8] dark:text-[#6EB8E1] border-2 border-[#6EB8E1] dark:border-[#5A7FC8] rounded-lg shadow-md hover:shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-6 py-2.5 bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white rounded-lg shadow-lg shadow-[#6EB8E1]/30 hover:shadow-xl hover:from-[#5A7FC8] hover:to-[#252E8A] transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {loading ? 'Saving...' : 'Save Pattern'}
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
