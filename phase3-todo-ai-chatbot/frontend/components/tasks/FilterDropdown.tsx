'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

interface FilterOption {
  value: string;
  label: string;
}

interface FilterDropdownProps {
  label: string;
  options: FilterOption[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  multiSelect?: boolean;
  icon?: React.ReactNode;
}

export function FilterDropdown({
  label,
  options,
  selectedValues,
  onChange,
  multiSelect = true,
  icon
}: FilterDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleToggle = (value: string) => {
    if (multiSelect) {
      if (selectedValues.includes(value)) {
        onChange(selectedValues.filter((v) => v !== value));
      } else {
        onChange([...selectedValues, value]);
      }
    } else {
      onChange([value]);
      setIsOpen(false);
    }
  };

  const handleClearAll = () => {
    onChange([]);
  };

  const activeCount = selectedValues.length;

  return (
    <div ref={dropdownRef} className="relative">
      {/* Trigger Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsOpen(!isOpen)}
        className={`
          flex items-center gap-2 px-4 py-3
          glass-card rounded-xl
          transition-all duration-300
          ${isOpen ? 'ring-2 ring-purple-500 shadow-lg shadow-purple-500/30' : ''}
          ${activeCount > 0 ? 'glow-purple' : ''}
        `}
      >
        {icon}
        <span className="font-medium text-gray-900 dark:text-white">
          {label}
        </span>
        {activeCount > 0 && (
          <motion.span
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-center w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold rounded-full"
          >
            {activeCount}
          </motion.span>
        )}
        <ChevronDown
          className={`w-4 h-4 text-gray-500 transition-transform duration-300 ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </motion.button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full left-0 mt-2 w-56 z-50"
          >
            <div className="glass-card rounded-xl shadow-2xl overflow-hidden border border-gray-200/50 dark:border-gray-700/50">
              {/* Header */}
              {multiSelect && activeCount > 0 && (
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/50">
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {activeCount} selected
                  </span>
                  <button
                    onClick={handleClearAll}
                    className="text-sm text-purple-500 dark:text-[#C8ABE6] hover:text-purple-600 dark:hover:text-[#C8ABE6] font-medium"
                  >
                    Clear all
                  </button>
                </div>
              )}

              {/* Options */}
              <div className="max-h-64 overflow-y-auto py-2">
                {options.map((option) => {
                  const isSelected = selectedValues.includes(option.value);

                  return (
                    <motion.button
                      key={option.value}
                      whileHover={{ backgroundColor: 'rgba(139, 92, 246, 0.1)' }}
                      onClick={() => handleToggle(option.value)}
                      className="w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors"
                    >
                      {/* Checkbox */}
                      <div
                        className={`
                          flex items-center justify-center
                          w-5 h-5 rounded border-2
                          transition-all duration-200
                          ${
                            isSelected
                              ? 'bg-gradient-to-r from-purple-500 to-pink-500 border-purple-500 dark:from-[#C8ABE6] dark:to-[#F8CEC0] dark:border-[#C8ABE6]'
                              : 'border-gray-300 dark:border-gray-600'
                          }
                        `}
                      >
                        {isSelected && (
                          <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                          >
                            <Check className="w-3 h-3 text-white" strokeWidth={3} />
                          </motion.div>
                        )}
                      </div>

                      {/* Label */}
                      <span
                        className={`
                          text-sm font-medium
                          ${
                            isSelected
                              ? 'text-gray-900 dark:text-white'
                              : 'text-gray-600 dark:text-gray-400'
                          }
                        `}
                      >
                        {option.label}
                      </span>
                    </motion.button>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
