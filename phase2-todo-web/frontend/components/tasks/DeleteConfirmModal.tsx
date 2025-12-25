'use client';

import { ConfirmModal } from '@/components/ui/Modal';
import { useUIStore } from '@/store';
import { useTasks } from '@/hooks/useTasks';

export function DeleteConfirmModal() {
  const {
    isDeleteConfirmModalOpen,
    closeDeleteConfirmModal,
    deletingTaskId,
    deletingTaskTitle,
  } = useUIStore();
  const { deleteTask } = useTasks();

  const handleConfirmDelete = async () => {
    if (deletingTaskId) {
      await deleteTask(deletingTaskId);
      closeDeleteConfirmModal();
    }
  };

  return (
    <ConfirmModal
      open={isDeleteConfirmModalOpen}
      onClose={closeDeleteConfirmModal}
      onConfirm={handleConfirmDelete}
      title="Delete Task"
      description={`Are you sure you want to delete "${deletingTaskTitle}"? This action cannot be undone.`}
      confirmText="Delete"
      cancelText="Cancel"
      confirmVariant="danger"
    />
  );
}