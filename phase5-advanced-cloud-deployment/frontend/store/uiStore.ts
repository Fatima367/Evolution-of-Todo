import { create } from 'zustand'

interface UIState {
  isSidebarOpen: boolean
  isSignUpModalOpen: boolean
  isLoginModalOpen: boolean
  isCreateTaskModalOpen: boolean
  isEditTaskModalOpen: boolean
  editingTaskId: string | null
  isDeleteConfirmModalOpen: boolean
  deletingTaskId: string | null
  deletingTaskTitle: string | null
  isAuditLogModalOpen: boolean
  theme: 'light' | 'dark'
  taskRefreshTrigger: number
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  openSignUpModal: () => void
  closeSignUpModal: () => void
  openLoginModal: () => void
  closeLoginModal: () => void
  openCreateTaskModal: () => void
  closeCreateTaskModal: () => void
  openEditTaskModal: (taskId: string) => void
  closeEditTaskModal: () => void
  openDeleteConfirmModal: (taskId: string, taskTitle: string) => void
  closeDeleteConfirmModal: () => void
  openAuditLogModal: () => void
  closeAuditLogModal: () => void
  toggleTheme: () => void
  setTheme: (theme: 'light' | 'dark') => void
  triggerTaskRefresh: () => void
}

// BroadcastChannel for cross-tab task refresh notifications
const taskChannel = typeof window !== 'undefined' ? new BroadcastChannel('task-refresh') : null

// Listen for task refresh events from other tabs
if (taskChannel) {
  taskChannel.onmessage = (event) => {
    if (event.data.type === 'TASK_CREATED' || event.data.type === 'TASK_UPDATED' || event.data.type === 'TASK_DELETED') {
      // Trigger a UI refresh by updating a trigger value
      useUIStore.setState((state) => ({ taskRefreshTrigger: (state.taskRefreshTrigger || 0) + 1 }))
    }
  }
}

// Initialize theme from localStorage or system preference
const getInitialTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined') {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    if (savedTheme) return savedTheme;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  return 'light';
};

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  isSignUpModalOpen: false,
  isLoginModalOpen: false,
  isCreateTaskModalOpen: false,
  isEditTaskModalOpen: false,
  editingTaskId: null,
  isDeleteConfirmModalOpen: false,
  deletingTaskId: null,
  deletingTaskTitle: null,
  isAuditLogModalOpen: false,
  theme: 'light', // Default to light for SSR
  taskRefreshTrigger: 0,

  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),

  openSignUpModal: () => set({ isSignUpModalOpen: true }),
  closeSignUpModal: () => set({ isSignUpModalOpen: false }),

  openLoginModal: () => set({ isLoginModalOpen: true }),
  closeLoginModal: () => set({ isLoginModalOpen: false }),

  openCreateTaskModal: () => set({ isCreateTaskModalOpen: true }),
  closeCreateTaskModal: () => set({ isCreateTaskModalOpen: false }),

  openEditTaskModal: (taskId) => set({ isEditTaskModalOpen: true, editingTaskId: taskId }),
  closeEditTaskModal: () => set({ isEditTaskModalOpen: false, editingTaskId: null }),

  openDeleteConfirmModal: (taskId, taskTitle) => set({ isDeleteConfirmModalOpen: true, deletingTaskId: taskId, deletingTaskTitle: taskTitle }),
  closeDeleteConfirmModal: () => set({ isDeleteConfirmModalOpen: false, deletingTaskId: null, deletingTaskTitle: null }),

  openAuditLogModal: () => set({ isAuditLogModalOpen: true }),
  closeAuditLogModal: () => set({ isAuditLogModalOpen: false }),

  toggleTheme: () => set((state) => {
    const newTheme = state.theme === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', newTheme);
    // Apply class to html immediately
    const root = document.documentElement;
    if (newTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    return { theme: newTheme };
  }),
  setTheme: (theme) => set((state) => {
    localStorage.setItem('theme', theme);
    // Apply class to html immediately
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    return { theme };
  }),
  triggerTaskRefresh: () => {
    // Update local state
    set((state) => ({ taskRefreshTrigger: (state.taskRefreshTrigger || 0) + 1 }))
    // Notify other tabs
    if (taskChannel) {
      taskChannel.postMessage({ type: 'TASK_CREATED' })
    }
  },
}))