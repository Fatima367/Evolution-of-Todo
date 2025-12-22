import { create } from 'zustand'

interface UIState {
  isSidebarOpen: boolean
  isSignUpModalOpen: boolean
  isLoginModalOpen: boolean
  isCreateTaskModalOpen: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void
  openSignUpModal: () => void
  closeSignUpModal: () => void
  openLoginModal: () => void
  closeLoginModal: () => void
  openCreateTaskModal: () => void
  closeCreateTaskModal: () => void
  toggleTheme: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  isSignUpModalOpen: false,
  isLoginModalOpen: false,
  isCreateTaskModalOpen: false,
  theme: 'light',

  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  setSidebarOpen: (open) => set({ isSidebarOpen: open }),

  openSignUpModal: () => set({ isSignUpModalOpen: true }),
  closeSignUpModal: () => set({ isSignUpModalOpen: false }),

  openLoginModal: () => set({ isLoginModalOpen: true }),
  closeLoginModal: () => set({ isLoginModalOpen: false }),

  openCreateTaskModal: () => set({ isCreateTaskModalOpen: true }),
  closeCreateTaskModal: () => set({ isCreateTaskModalOpen: false }),

  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
  setTheme: (theme) => set({ theme }),
}))
