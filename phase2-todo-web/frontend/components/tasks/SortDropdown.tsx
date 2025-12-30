'use client';

import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ArrowUp, ArrowDown, Calendar, AlertCircle, Type } from 'lucide-react';
import { SortOption, SortField, SortDirection, SortConfig } from '../../lib/types';

interface SortDropdownProps {
  currentSort: SortOption;
  onChange: (sort: SortOption) => void;
  onToggleDirection: () => void;
}

const SORT_CONFIGS: SortConfig[] = [
  {
    label: 'Due Date',
    value: 'due_date',
    icon: 'Calendar',
    defaultDirection: 'asc'
  },
  {
    label: 'Priority',
    value: 'priority',
    icon: 'AlertCircle',
    defaultDirection: 'desc'
  },
  {
    label: 'Alphabetical',
    value: 'title',
    icon: 'Type',
    defaultDirection: 'asc'
  }
];

/**
 * SortDropdown component for task sorting with accessibility features
 */
export function SortDropdown({ currentSort, onChange, onToggleDirection }: SortDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [focusedIndex, setFocusedIndex] = useState(0);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const optionsRef = useRef<(HTMLButtonElement | null)[]>([]);

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

  /**
   * Handle keyboard navigation
   */
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>) => {
    if (!isOpen) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (event.key) {
      case 'Escape':
        event.preventDefault();
        setIsOpen(false);
        break;
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex((prev) => (prev + 1) % SORT_CONFIGS.length);
        break;
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex((prev) => (prev - 1 + SORT_CONFIGS.length) % SORT_CONFIGS.length);
        break;
      case 'Enter':
        event.preventDefault();
        selectSort(SORT_CONFIGS[focusedIndex].value);
        break;
    }
  };

  /**
   * Select a sort field
   */
  const selectSort = (field: SortField) => {
    const config = SORT_CONFIGS.find(c => c.value === field);
    if (config) {
      onChange({
        field,
        direction: config.defaultDirection
      });
    }
    setIsOpen(false);
  };

  /**
   * Get current sort configuration
   */
  const currentConfig = SORT_CONFIGS.find(c => c.value === currentSort.field);

  /**
   * Get icon for sort field
   */
  const getSortIcon = (config: SortConfig) => {
    switch (config.icon) {
      case 'Calendar':
        return <Calendar className="w-4 h-4" />;
      case 'AlertCircle':
        return <AlertCircle className="w-4 h-4" />;
      case 'Type':
        return <Type className="w-4 h-4" />;
      default:
        return <ArrowUpDown className="w-4 h-4" />;
    }
  };

  /**
   * Get icon for sort direction - shows what will happen after click
   */
  const getToggleIcon = () => {
    // If currently ascending, show down arrow (will sort descending after click)
    // If currently descending, show up arrow (will sort ascending after click)
    return currentSort.direction === 'asc' ? (
      <ArrowDown className="w-4 h-4 text-[#5A7FC8] dark:text-[#C8ABE6]" />
    ) : (
      <ArrowUp className="w-4 h-4 text-[#5A7FC8] dark:text-[#C8ABE6]" />
    );
  };

  return (
    <div ref={dropdownRef} className="relative">
      {/* Sort Control Container */}
      <div className="flex items-center gap-2">
        {/* Trigger Button - Opens Dropdown */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => setIsOpen(!isOpen)}
          onKeyDown={handleKeyDown}
          aria-label={`Sort by ${currentConfig?.label || 'Default'}`}
          aria-expanded={isOpen}
          aria-haspopup="listbox"
          role="button"
          className={`
            flex items-center gap-2 px-4 py-2.5
            glass-card rounded-xl
            transition-all duration-300
            ${isOpen ? 'ring-2 ring-[#5A7FC8] dark:ring-[#C8ABE6] shadow-lg shadow-[#6EB8E1]/30' : 'hover:shadow-md'}
          `}
        >
          {/* Sort Field Icon */}
          {currentConfig && getSortIcon(currentConfig)}

          {/* Sort Label */}
          <span className="font-medium text-gray-900 dark:text-white min-w-[120px] text-left">
            {currentConfig?.label || 'Default'}
          </span>

          {/* Direction Chevron */}
          <ChevronDown
            className={`w-4 h-4 text-gray-500 transition-transform duration-300 ${
              isOpen ? 'rotate-180' : ''
            }`}
          />
        </motion.button>

        {/* Direction Toggle Button - Separate, Not Nested */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onToggleDirection}
          aria-label={`Toggle sort direction - Currently ${currentSort.direction === 'asc' ? 'Ascending' : 'Descending'}`}
          className="flex items-center justify-center w-8 h-8 rounded-full hover:bg-[#D6E6F2]/50 dark:hover:bg-[#201761]/50 transition-colors"
          title={`Click to sort ${currentSort.direction === 'asc' ? 'Descending' : 'Ascending'}`}
          style={{ pointerEvents: isOpen ? 'none' : 'auto' }}
        >
          {getToggleIcon()}
        </motion.button>
      </div>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="absolute top-full right-0 mt-2 w-64 z-50"
            role="listbox"
            aria-activedescendant={SORT_CONFIGS[focusedIndex].value}
          >
            <div className="glass-card rounded-xl shadow-2xl overflow-hidden border border-gray-200/50 dark:border-gray-700/50">
              {/* Header */}
              <div className="px-4 py-3 border-b border-gray-200/50 dark:border-gray-700/50 bg-gray-50/50 dark:bg-gray-900/50">
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  Sort by
                </span>
              </div>

              {/* Options */}
              <div className="max-h-64 overflow-y-auto py-2">
                {SORT_CONFIGS.map((config, index) => {
                  const isSelected = currentSort.field === config.value;
                  const isFocused = focusedIndex === index;

                  return (
                    <motion.button
                      key={config.value}
                      ref={(el) => {
                        optionsRef.current[index] = el;
                      }}
                      role="option"
                      aria-selected={isSelected}
                      whileHover={{ backgroundColor: 'rgba(90, 127, 200, 0.08)' }}
                      onClick={() => selectSort(config.value)}
                      onMouseEnter={() => setFocusedIndex(index)}
                      className={`
                        w-full flex items-center gap-3 px-4 py-3
                        text-left transition-colors outline-none
                        ${isFocused ? 'bg-[#D6E6F2]/50 dark:bg-[#201761]/50' : ''}
                        ${
                          isSelected
                            ? 'bg-gradient-to-r from-[#6EB8E1] to-[#5A7FC8] text-white'
                            : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
                        }
                      `}
                    >
                      {/* Icon */}
                      <span className={isSelected ? 'text-white' : 'text-[#5A7FC8] dark:text-[#C8ABE6]'}>
                        {getSortIcon(config)}
                      </span>

                      {/* Label */}
                      <span className="text-sm font-medium">
                        {config.label}
                      </span>

                      {/* Selected indicator */}
                      {isSelected && (
                        <motion.div
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className="ml-auto"
                        >
                          <div className="w-2 h-2 rounded-full bg-white shadow-lg" />
                        </motion.div>
                      )}
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
