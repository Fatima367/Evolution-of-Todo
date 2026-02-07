'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, History, AlertCircle, CheckCircle2, PlusCircle, Pencil, Trash2 } from 'lucide-react';
import { useUIStore } from '@/store/uiStore';
import { formatRelativeTime } from '@/lib/utils';
import { apiClient } from '@/lib/api';

interface AuditLog {
  id: number;
  task_id: string | null;
  operation: string;
  changes: any;
  created_at: string;
}

export function AuditLogModal() {
  const isOpen = useUIStore((state) => state.isAuditLogModalOpen);
  const closeModal = useUIStore((state) => state.closeAuditLogModal);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchLogs();
    }
  }, [isOpen]);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getAuditLogs();
      setLogs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getOperationIcon = (operation: string) => {
    switch (operation) {
      case 'created': return <PlusCircle size={16} className="text-green-500" />;
      case 'updated': return <Pencil size={16} className="text-blue-500" />;
      case 'completed': return <CheckCircle2 size={16} className="text-purple-500" />;
      case 'deleted': return <Trash2 size={16} className="text-red-500" />;
      default: return <History size={16} className="text-gray-500" />;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={closeModal}
          className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.9, opacity: 0, y: 20 }}
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-2xl max-h-[80vh] glass-card rounded-2xl shadow-2xl overflow-hidden flex flex-col bg-white dark:bg-gray-900"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200/50 dark:border-gray-700/50">
              <div className="flex items-center gap-3">
                <History size={24} className="text-[#6EB8E1]" />
                <h2 className="text-xl font-bold bg-gradient-to-r from-[#163cb7] to-[#149c8c] dark:from-[#6EB8E1] dark:to-[#4EB5A9] bg-clip-text text-transparent">
                  Activity Log
                </h2>
              </div>
              <button onClick={closeModal} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <X size={24} className="text-gray-500" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6">
              {loading ? (
                <div className="flex justify-center py-10">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#6EB8E1]"></div>
                </div>
              ) : error ? (
                <div className="flex items-center gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-600">
                  <AlertCircle size={20} />
                  <p>{error}</p>
                </div>
              ) : logs.length === 0 ? (
                <p className="text-center py-10 text-gray-500">No activity recorded yet.</p>
              ) : (
                <div className="space-y-4">
                  {logs.map((log) => (
                    <div key={log.id} className="flex items-start gap-3 p-3 rounded-xl border border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                      <div className="mt-1">{getOperationIcon(log.operation)}</div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                          Task {log.operation}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                          {formatRelativeTime(log.created_at)}
                        </p>
                        {log.changes && log.changes.title && (
                          <p className="text-xs text-gray-600 dark:text-gray-300 mt-1 italic truncate">
                            "{log.changes.title}"
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
