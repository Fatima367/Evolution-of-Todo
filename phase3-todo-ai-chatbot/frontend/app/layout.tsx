import type { Metadata } from 'next'
import { Inter, Space_Grotesk } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/components/providers/QueryProvider'
import { AuthProvider } from '@/contexts/auth'
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { SignUpModal } from '@/components/auth/SignUpModal'
import { LoginModal } from '@/components/auth/LoginModal'
import { CreateTaskModal } from '@/components/tasks/CreateTaskModal'
import { FloatingChatButton } from '@/components/chat/FloatingChatButton'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'TodoBoard - Evolve Your Workflow',
  description: 'From simple lists to intelligent insights, the last todo app you\'ll ever need.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
      </head>
      <body className={`${inter.variable} ${spaceGrotesk.variable} font-sans`}>
          <AuthProvider>
            <ThemeProvider>
              <QueryProvider>
                {children}

                {/* Global Modals */}
                <SignUpModal />
                <LoginModal />
                <CreateTaskModal />

                {/* AI Chat Assistant */}
                <FloatingChatButton />
              </QueryProvider>
            </ThemeProvider>
          </AuthProvider>
      </body>
    </html>
  )
}
