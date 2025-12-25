'use client';

import { useState, useEffect } from 'react';
import { Modal } from '@/components/ui/Modal';
import { TaskForm } from './TaskForm';
import { useUIStore } from '@/store';
import { useTasks } from '@/hooks/useTasks';
import type { Task } from '@/lib/types';

export function EditTaskModal() {
  const { isEditTaskModalOpen, closeEditTaskModal, editingTaskId } = useUIStore();
  const { tasks, updateTask, loading } = useTasks();
  const [taskToEdit, setTaskToEdit] = useState<Task | null>(null);

  const handleClose = () => {
    setTaskToEdit(null);
    closeEditTaskModal();
  };

  // Find the task to edit when modal opens or editingTaskId changes
  useEffect(() => {
    if (editingTaskId) {
      const task = tasks.find(t => t.id === editingTaskId);
      if (task) {
        setTaskToEdit(task);
      } else if (!loading && tasks.length > 0) {
        // If tasks are loaded but the specific task is not found, it might have been deleted
        // In this case, close the modal
        handleClose();
      }
    }
  }, [editingTaskId, tasks, loading, handleClose]);

  const handleUpdateTask = async (data: any) => {
    if (taskToEdit) {
      await updateTask(taskToEdit.id, {
        title: data.title,
        description: data.description,
        priority: data.priority,
      });
      closeEditTaskModal();
    }
  };

  // Close modal when task is updated successfully
  useEffect(() => {
    if (taskToEdit && !tasks.some(t => t.id === taskToEdit.id)) {
      // If the task was deleted, close the modal
      handleClose();
    }
  }, [tasks, taskToEdit, handleClose]);

  return (
    <Modal
      open={isEditTaskModalOpen}
      onClose={handleClose}
      title="Edit Task"
      size="md"
      showCloseButton={true}
    >
      {taskToEdit ? (
        <TaskForm
          onSubmit={handleUpdateTask}
          onCancel={handleClose}
          initialData={{
            title: taskToEdit.title,
            description: taskToEdit.description,
            priority: taskToEdit.priority,
          }}
        />
      ) : editingTaskId && tasks.length === 0 ? (
        <div className="py-4">
          <div className="text-center">
            <p className="text-gray-600 dark:text-gray-400">Loading tasks...</p>
          </div>
        </div>
      ) : (
        <div className="py-4">
          <div className="animate-pulse flex flex-col space-y-4">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
          </div>
        </div>
      )}
    </Modal>
  );
}