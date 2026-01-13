'use client';

import { SearchBar } from '../tasks/SearchBar';
import { FilterDropdown } from '../tasks/FilterDropdown';
import { SortDropdown } from '../tasks/SortDropdown';
import { AlertCircle, Calendar, Tag as TagIcon } from 'lucide-react';
import type { TaskPriority, TaskStatus, SortOption } from '@/lib/types';

interface FilterPanelProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  selectedPriorities: TaskPriority[];
  onPrioritiesChange: (priorities: TaskPriority[]) => void;
  selectedStatuses: TaskStatus[];
  onStatusesChange: (statuses: TaskStatus[]) => void;
  selectedTags: string[];
  onTagsChange: (tags: string[]) => void;
  availableTags: string[];
  currentSort: SortOption;
  onSortChange: (sort: SortOption) => void;
  onToggleSortDirection: () => void;
}

export function FilterPanel({
  searchQuery,
  onSearchChange,
  selectedPriorities,
  onPrioritiesChange,
  selectedStatuses,
  onStatusesChange,
  selectedTags,
  onTagsChange,
  availableTags,
  currentSort,
  onSortChange,
  onToggleSortDirection,
}: FilterPanelProps) {
  const priorityOptions = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' },
  ];

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
  ];

  const tagOptions = availableTags.map(tag => ({
    value: tag,
    label: tag,
  }));

  return (
    <div className="space-y-4">
      {/* Search Bar */}
      <SearchBar
        value={searchQuery}
        onChange={onSearchChange}
        placeholder="Search tasks by title or description..."
      />

      {/* Filter and Sort Controls */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Priority Filter */}
        <FilterDropdown
          label="Priority"
          options={priorityOptions}
          selectedValues={selectedPriorities}
          onChange={onPrioritiesChange}
          multiSelect={true}
          icon={<AlertCircle className="w-4 h-4 text-orange-500" />}
        />

        {/* Status Filter */}
        <FilterDropdown
          label="Status"
          options={statusOptions}
          selectedValues={selectedStatuses}
          onChange={onStatusesChange}
          multiSelect={true}
          icon={<Calendar className="w-4 h-4 text-blue-500" />}
        />

        {/* Tags Filter */}
        {availableTags.length > 0 && (
          <FilterDropdown
            label="Tags"
            options={tagOptions}
            selectedValues={selectedTags}
            onChange={onTagsChange}
            multiSelect={true}
            icon={<TagIcon className="w-4 h-4 text-green-500" />}
          />
        )}

        {/* Sort Dropdown */}
        <div className="ml-auto">
          <SortDropdown
            currentSort={currentSort}
            onChange={onSortChange}
            onToggleDirection={onToggleSortDirection}
          />
        </div>
      </div>
    </div>
  );
}
