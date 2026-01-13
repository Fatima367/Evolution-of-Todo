'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trash2, X, AlertTriangle } from 'lucide-react';
import { useUIStore } from '@/store/uiStore';
import { useTasks } from '@/hooks/useTasks';

export function DeleteConfirmModal() {
  const {
    isDeleteConfirmModalOpen,
    closeDeleteConfirmModal,
    deletingTaskId,
    deletingTaskTitle,
  } = useUIStore();
  const { deleteTask } = useTasks();

  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirmDelete = async () => {
    if (deletingTaskId) {
      setIsDeleting(true);
      try {
        await deleteTask(deletingTaskId);
      } finally {
        setIsDeleting(false);
        closeDeleteConfirmModal();
      }
    }
  };

  return (
    <AnimatePresence>
      {isDeleteConfirmModalOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={closeDeleteConfirmModal}
          className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md glass-card rounded-2xl shadow-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200/50 dark:border-gray-700/50">
              <h2 className="text-xl sm:text-2xl font-bold text-red-600">Delete Task</h2>
              <motion.button
                whileHover={{ scale: 1.1, rotate: 90 }}
                whileTap={{ scale: 0.9 }}
                onClick={closeDeleteConfirmModal}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                aria-label="Close modal"
              >
                <X size={24} className="text-gray-500 dark:text-gray-400" />
              </motion.button>
            </div>

            {/* Content */}
            <div className="p-4 sm:p-6">
              {/* Warning Icon */}
              <div className="flex justify-center mb-4">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', delay: 0.1 }}
                  className="w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center"
                >
                  <AlertTriangle size={32} className="text-red-600 dark:text-red-400" />
                </motion.div>
              </div>

              {/* Warning Text */}
              <div className="text-center space-y-3 mb-6">
                <p className="text-gray-700 dark:text-gray-300 text-lg font-medium">
                  Are you sure you want to delete this task?
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-sm">
                  "{deletingTaskTitle}"
                </p>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  This action cannot be undone.
                </p>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={closeDeleteConfirmModal}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 glass-card rounded-xl font-semibold text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Cancel
                </motion.button>
                <motion.button
                  type="button"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleConfirmDelete}
                  disabled={isDeleting}
                  className="flex-1 px-6 py-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {isDeleting ? (
                    <>
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      >
                        <Trash2 size={18} />
                      </motion.div>
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 size={18} />
                      Delete
                    </>
                  )}
                </motion.button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
