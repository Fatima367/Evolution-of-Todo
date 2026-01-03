'use client'

import { useState, useEffect, useRef } from 'react'
import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { X, MessageCircleMore, SquarePen } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { useUIStore } from '@/store'

// Dynamic theme config based on current theme
const getChatKitTheme = (isDark: boolean) => ({
  colorScheme: isDark ? 'dark' : 'light',
  radius: 'round',
  color: {
    grayscale: { hue: isDark ? 220 : 210, tint: isDark ? 6 : 4, shade: isDark ? 1 : 0 },
    accent: { primary: '#6EB8E1', level: 1 },
  },
} as const)

export function FloatingChatButton() {
  const { user } = useAuth()
  const theme = useUIStore((state) => state.theme)
  const triggerTaskRefresh = useUIStore((state) => state.triggerTaskRefresh)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [initialThread, setInitialThread] = useState<string | null>(null)
  const [isReady, setIsReady] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [lastMessageCount, setLastMessageCount] = useState(0)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Safe theme check with default
  const isDark = theme === 'dark'

  // Listen for task creation messages from ChatKit and trigger refresh
  useEffect(() => {
    if (!isChatOpen) return

    // Check for task-related messages in the chat
    const checkForTaskCreation = () => {
      const messages = document.querySelectorAll('.chatkit-wrapper [data-content-type="output_text"]')
      const currentCount = messages.length

      if (currentCount > lastMessageCount) {
        // New assistant message added
        const latestMessage = messages[messages.length - 1]
        const text = latestMessage?.textContent?.toLowerCase() || ''

        // Check if the message indicates a task was created
        const taskCreatedPatterns = [
          'task created successfully',
          'i\'ve added the task',
          'i\'ve created the task',
          'added a new task',
          'created task',
          'new task added',
          'task has been created',
        ]

        const isTaskCreated = taskCreatedPatterns.some(pattern => text.includes(pattern))

        if (isTaskCreated) {
          console.log('📋 Task creation detected, triggering refresh...')
          triggerTaskRefresh()
        }

        setLastMessageCount(currentCount)
      }
    }

    // Check periodically for new messages
    const interval = setInterval(checkForTaskCreation, 500)

    // Also observe for DOM changes
    const wrapper = document.querySelector('.chatkit-wrapper')
    if (wrapper) {
      const observer = new MutationObserver(checkForTaskCreation)
      observer.observe(wrapper, { childList: true, subtree: true })
      return () => {
        observer.disconnect()
        clearInterval(interval)
      }
    }

    return () => clearInterval(interval)
  }, [isChatOpen, lastMessageCount, triggerTaskRefresh])

  // Handle SSR mounting
  useEffect(() => {
    setMounted(true)
    if (user) {
      const savedThread = localStorage.getItem(`chatkit-thread-${user.id}`)
      setInitialThread(savedThread)
    }
    setIsReady(true)
  }, [user])

  const { control } = useChatKit({
    api: {
      url: process.env.NEXT_PUBLIC_API_URL
        ? `${process.env.NEXT_PUBLIC_API_URL}/chatkit`
        : 'http://127.0.0.1:8000/chatkit',
      domainKey: 'localhost',
      fetch: async (input, init) => {
        const token = localStorage.getItem('auth_token')
        const headers = {
          ...init?.headers,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        }
        return fetch(input, { ...init, headers })
      },
    },
    initialThread: initialThread || undefined,
    theme: getChatKitTheme(isDark),
    startScreen: {
      greeting: 'Welcome! I can help you manage your tasks.',
      prompts: [
        { label: 'Add Task', prompt: 'Add a new task to buy groceries' },
        { label: 'List Tasks', prompt: 'Show me all my pending tasks' },
        { label: 'Help', prompt: 'What can you help me with?' },
      ],
    },
    composer: {
      placeholder: 'Ask me to manage your tasks...',
    },
    onThreadChange: ({ threadId }) => {
      if (threadId && user) {
        localStorage.setItem(`chatkit-thread-${user.id}`, threadId)
      }
    },
    onError: ({ error }) => {
      console.error('ChatKit error:', error)
    },
  })

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [])

  // Apply custom send icon using DOM manipulation
  useEffect(() => {
    if (!isChatOpen) return

    const applyCustomIcon = () => {
      const wrapper = document.querySelector('.chatkit-wrapper')
      if (!wrapper) return

      // Find the send button (type="submit" in the composer)
      const submitButtons = wrapper.querySelectorAll('button[type="submit"]')

      submitButtons.forEach((button) => {
        if (button instanceof HTMLElement) {
          // Hide default SVG icons
          const svgs = button.querySelectorAll('svg');
          svgs.forEach((svg) => {
            if (svg instanceof SVGElement) {
              svg.style.cssText = 'display: none !important; width: 0 !important; height: 0 !important;';
            }
          });

          // Add custom paper plane icon if not already present
          if (!button.querySelector('.custom-send-icon')) {
            const iconSpan = document.createElement('span');
            iconSpan.className = 'custom-send-icon';
            iconSpan.innerHTML = '<svg viewBox="0 0 576 512" style="display:block !important; width:18px !important; height:18px !important;"><path fill="currentColor" d="M482.3 192c34.2 0 64-26.2 64-58.8c0-32.7-29.8-59.2-64-59.2L128 65.7c-38.6 0-69.8 31.1-69.8 69.5c0 32.7 26.4 59.2 64 59.2l37.8 0c3.4 0 6.1 2.7 6.1 6.1c0 1.3-.4 2.5-1.1 3.4l-14.6 21.8c-1.4 2.1-1.4 4.7 0 6.8l14.6 21.8c.7.9 1.1 2.1 1.1 3.4c0 3.4-2.7 6.1-6.1 6.1l-37.8 0c-3.4 0-6.1-2.7-6.1-6.1c0-32.7-26.4-59.2-64-59.2L64 134c-38.6 0-69.8 31.1-69.8 69.5c0 32.7 26.4 59.2 64 59.2l290.3 0c34.2 0 64-26.2 64-58.8c0-32.7-29.8-59.2-64-59.2zM256 352c-53 0-96-43-96-96s43-96 96-96s96 43 96 96s-43 96-96 96zm224 64H160c-17.7 0-32 14.3-32 32v48h64V448h128v48h64v-48c0-17.7-14.3-32-32-32z"/></svg>';
            iconSpan.style.cssText = 'display:flex !important; align-items:center !important; justify-content:center !important; width:100% !important; height:100% !important;';
            
            button.style.cssText = 'position:relative !important; display:flex !important; align-items:center !important; justify-content:center !important;';
            button.appendChild(iconSpan);
          }
        }
      });
    }

    // Initial application with multiple attempts
    const timeouts = [100, 300, 500, 1000].map(delay =>
      setTimeout(applyCustomIcon, delay)
    )

    // Watch for DOM changes
    const observer = new MutationObserver(applyCustomIcon)
    const wrapper = document.querySelector('.chatkit-wrapper')
    if (wrapper) {
      observer.observe(wrapper, {
        childList: true,
        subtree: true,
      })
    }

    return () => {
      timeouts.forEach(clearTimeout)
      observer.disconnect()
    }
  }, [isChatOpen])

  // Check if user is logged in (has valid token) - only after mount
  const hasToken = mounted && !!localStorage.getItem('auth_token')

  // Only show chat button for authenticated users (after mount to prevent hydration mismatch)
  if (!mounted || !user || !isReady || !hasToken) {
    return null
  }


  return (
    <>
      {/* Floating Chat Button (bottom-right) */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-8 right-8 w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 border-none cursor-pointer shadow-lg shadow-cyan-400/40 flex items-center justify-center z-[100] hover:scale-110 transition-transform duration-200 animate-pulse-glow"
          aria-label="Open AI Assistant"
        >
          <MessageCircleMore className="w-7 h-7 text-white" />
        </button>
      )}

      {/* Chat Popup (bottom-right) */}
      {isChatOpen && (
        <>
          {/* Backdrop */}
          <div
            onClick={() => setIsChatOpen(false)}
            className="fixed inset-0 bg-black/30 backdrop-blur-sm z-[999]"
          />

          {/* Popup Window */}
          <div
            className={`fixed bottom-8 right-8 w-[420px] h-[600px] max-w-[calc(100vw-4rem)] max-h-[calc(100vh-4rem)] rounded-2xl shadow-2xl shadow-black/50 flex flex-col overflow-hidden z-[1000] animate-popup-in ${
              isDark
                ? 'bg-[#16213e] border border-gray-700/50'
                : 'bg-white dark:bg-[#16213e] border border-gray-200 dark:border-gray-700/50'
            }`}
          >
            {/* Header */}
            <div className={`p-4 flex justify-between items-center border-b ${
              isDark
                ? 'bg-[#0f3460] border-cyan-400/20'
                : 'bg-white border-gray-200'
            }`}>
              <div className="flex items-center gap-3">
                <SquarePen className={`w-5 h-5 ${isDark ? 'text-cyan-400' : 'text-[#6EB8E1]'}`} />
                <span className={`text-lg font-bold ${isDark ? 'text-cyan-400' : 'bg-gradient-to-r from-[#6EB8E1] to-[#4EB5A9] bg-clip-text text-transparent'}`}>Todo Assistant</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setIsChatOpen(false)}
                  className={`p-3 rounded-lg transition-colors duration-200 ${
                    isDark
                      ? 'hover:bg-white/10 text-gray-400 hover:text-white'
                      : 'hover:bg-gray-100 text-gray-500 hover:text-gray-700'
                  }`}
                  aria-label="Close chat"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Chat Content */}
            <div className="flex-1 overflow-hidden flex flex-col chatkit-wrapper">
              <ChatKit control={control} className="h-full w-full" />
              <div ref={messagesEndRef} />
            </div>
          </div>
        </>
      )}

      <style jsx global>{`
        @keyframes popupIn {
          from {
            opacity: 0;
            transform: scale(0.9) translateY(20px);
          }
          to {
            opacity: 1;
            transform: scale(1) translateY(0);
          }
        }

        @keyframes pulseGlow {
          0%, 100% {
            box-shadow: 0 4px 20px rgba(76, 201, 240, 0.4);
          }
          50% {
            box-shadow: 0 4px 30px rgba(76, 201, 240, 0.7);
          }
        }

        .animate-popup-in {
          animation: popupIn 0.25s ease-out;
        }

        .animate-pulse-glow {
          animation: pulseGlow 2s ease-in-out infinite;
        }

        /* Hide default icons in ChatKit */
        .chatkit-wrapper svg,
        .chatkit-wrapper button svg,
        .chatkit-wrapper button[type="submit"] svg {
          opacity: 0 !important;
          width: 0 !important;
          height: 0 !important;
          display: none !important;
        }

        /* Paper plane icon styling */
        .chatkit-wrapper button[type="submit"] {
          position: relative !important;
        }

        .chatkit-wrapper button[type="submit"] .custom-send-icon svg {
          display: block !important;
          opacity: 1 !important;
          width: 18px !important;
          height: 18px !important;
        }

        /* Light mode welcome text styling */
        .chatkit-wrapper .chatkit-start-screen h2,
        .chatkit-wrapper .chatkit-start-screen .font-semibold {
          color: #0f3460 !important;
          font-weight: 700 !important;
        }

        .chatkit-wrapper .chatkit-start-screen p,
        .chatkit-wrapper .chatkit-start-screen .text-sm {
          color: #475569 !important;
        }

        /* Light mode gradient text */
        .chatkit-wrapper .chatkit-start-screen .bg-gradient-to-r {
          background: linear-gradient(to right, #6EB8E1, #4EB5A9) !important;
          -webkit-background-clip: text !important;
          -webkit-text-fill-color: transparent !important;
          background-clip: text !important;
        }

        /* Dark mode adjustments */
        .dark .chatkit-wrapper .chatkit-start-screen h2,
        .dark .chatkit-wrapper .chatkit-start-screen .font-semibold {
          color: #4cc9f0 !important;
        }

        .dark .chatkit-wrapper .chatkit-start-screen p,
        .dark .chatkit-wrapper .chatkit-start-screen .text-sm {
          color: #94a3b8 !important;
        }

        /* Style prompt buttons in light mode */
        .chatkit-wrapper .chatkit-start-screen button {
          background: linear-gradient(to right, #6EB8E1, #4EB5A9) !important;
          color: white !important;
          font-weight: 600 !important;
          border: none !important;
        }

        /* Send button styling in light mode */
        .chatkit-wrapper button[type="submit"]:not(.custom-send-icon) {
          background: linear-gradient(to right, #6EB8E1, #4EB5A9) !important;
          border: none !important;
        }

        .chatkit-wrapper button[type="submit"]:not(.custom-send-icon)::before {
          content: '✈' !important;
          font-size: 16px !important;
          color: white !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
        }

        .chatkit-wrapper button[type="submit"]:not(.custom-send-icon) svg {
          display: none !important;
        }
      `}</style>
    </>
  )
}