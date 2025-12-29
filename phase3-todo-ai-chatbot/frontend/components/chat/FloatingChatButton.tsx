'use client'

import { useState, useEffect, useRef, useMemo } from 'react'
import { ChatKit, useChatKit } from '@openai/chatkit-react'
import { MessageCircle, X, RefreshCw, Send } from 'lucide-react'
import { useAuth } from '@/hooks/useAuth'
import { FaPaperPlane } from 'react-icons/fa'

export function FloatingChatButton() {
  const { user } = useAuth()
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [initialThread, setInitialThread] = useState<string | null>(null)
  const [isReady, setIsReady] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (user) {
      const savedThread = localStorage.getItem(`chatkit-thread-${user.id}`)
      setInitialThread(savedThread)
    }
    setIsReady(true)
  }, [user])

  // Memoize the send button icon to prevent re-renders
  const sendButtonIcon = useMemo(() => <FaPaperPlane className="w-4 h-4" />, [])

  const { control } = useChatKit({
    api: {
      url: process.env.NEXT_PUBLIC_API_URL
        ? `${process.env.NEXT_PUBLIC_API_URL}/chatkit`
        : 'http://127.0.0.1:8000/chatkit',
      domainKey: 'localhost',
      fetch: async (input, init) => {
        // Get JWT token from localStorage (managed by Better Auth)
        const token = localStorage.getItem('token')
        const headers = {
          ...init?.headers,
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        }
        return fetch(input, { ...init, headers })
      },
    },
    initialThread: initialThread || undefined,
    theme: {
      colorScheme: 'dark',
      color: {
        grayscale: { hue: 220, tint: 6, shade: -1 },
        accent: { primary: '#4cc9f0', level: 1 },
      },
      radius: 'round',
    },
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
      sendButton: {
        icon: sendButtonIcon,
      },
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

  const handleNewChat = () => {
    if (user) {
      localStorage.removeItem(`chatkit-thread-${user.id}`)
    }
    window.location.reload()
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [])

  // Only show chat button for authenticated users
  if (!user || !isReady) return null

  return (
    <>
      {/* Floating Chat Button (bottom-right) */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-8 right-8 w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-cyan-400 border-none cursor-pointer shadow-lg shadow-cyan-400/40 flex items-center justify-center z-[100] hover:scale-110 transition-transform duration-200 animate-pulse-glow"
          aria-label="Open AI Assistant"
        >
          <MessageCircle className="w-7 h-7 text-white" />
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
            className="fixed bottom-8 right-8 w-[420px] h-[600px] max-w-[calc(100vw-4rem)] max-h-[calc(100vh-4rem)] bg-[#16213e] rounded-2xl shadow-2xl shadow-black/50 flex flex-col overflow-hidden z-[1000] animate-popup-in"
          >
            {/* Header */}
            <div className="p-4 bg-[#0f3460] flex justify-between items-center border-b border-cyan-400/20">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                <span className="text-cyan-400 font-semibold">Todo Assistant</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleNewChat}
                  className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded-lg transition-colors duration-200 flex items-center gap-1.5"
                  title="Start new conversation"
                >
                  <RefreshCw className="w-3 h-3" />
                  New Chat
                </button>
                <button
                  onClick={() => setIsChatOpen(false)}
                  className="p-3 hover:bg-white/10 text-gray-400 hover:text-white rounded-lg transition-colors duration-200"
                  aria-label="Close chat"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Chat Content */}
            <div className="flex-1 overflow-hidden flex flex-col">
              <ChatKit control={control} className="h-full w-full" />
              <div ref={messagesEndRef} />
            </div>
          </div>
        </>
      )}

      <style jsx>{`
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
      `}</style>
    </>
  )
}
