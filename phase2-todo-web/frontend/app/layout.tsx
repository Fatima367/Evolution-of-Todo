import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/components/providers/QueryProvider'
import { SignUpModal } from '@/components/auth/SignUpModal'
import { LoginModal } from '@/components/auth/LoginModal'
import { CreateTaskModal } from '@/components/tasks/CreateTaskModal'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'TodoEvo - Evolve Your Workflow',
  description: 'From simple lists to intelligent insights, the last todo app you\'ll ever need.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={inter.className}>
        <QueryProvider>
          {children}

          {/* Global Modals */}
          <SignUpModal />
          <LoginModal />
          <CreateTaskModal />
        </QueryProvider>
      </body>
    </html>
  )
}
