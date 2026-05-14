import type { Metadata } from 'next'
import './globals.css'
import { QueryProvider } from '@/components/providers/QueryProvider'
import { AuthProvider } from '@/contexts/auth'
import { ThemeProvider } from '@/components/providers/ThemeProvider'
import { NotificationProvider } from '@/components/providers/NotificationProvider'
import { SignUpModal } from '@/components/auth/SignUpModal'
import { LoginModal } from '@/components/auth/LoginModal'
import { CreateTaskModal } from '@/components/tasks/CreateTaskModal'
import { AuditLogModal } from '@/components/tasks/AuditLogModal'
import { FloatingChatButton } from '@/components/chat/FloatingChatButton'

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
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Space+Grotesk:wght@300..700&display=swap"
          rel="stylesheet"
        />
        <script src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js" async></script>
      </head>
      <body className="font-sans"
        style={{
          fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }}>
          <AuthProvider>
            <ThemeProvider>
              <QueryProvider>
                <NotificationProvider>
                  {children}

                  {/* Global Modals */}
                                  <SignUpModal />
                                  <LoginModal />
                                  <CreateTaskModal />
                                  <AuditLogModal />
                  
                                  {/* AI Chat Assistant */}                  <FloatingChatButton />
                </NotificationProvider>
              </QueryProvider>
            </ThemeProvider>
          </AuthProvider>
      </body>
    </html>
  )
}