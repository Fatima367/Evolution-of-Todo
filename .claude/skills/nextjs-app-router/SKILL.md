---
name: Next.js App Router Skill
description: Expert skill for building modern Next.js 16+ applications using the App Router, Server Components, TypeScript, and Tailwind CSS. Optimized for the Evolution of Todo hackathon frontend.
tags: [nextjs, react, typescript, tailwind, app-router, frontend, server-components]
---

# Next.js 16+ App Router Skill

## Overview

This skill provides expertise in building modern, performant frontend applications using:
- **Next.js 16+** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Server Components** - Default rendering strategy
- **Better Auth** - Authentication integration

## Core Capabilities

### 1. Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── (auth)/                 # Auth group
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── signup/
│   │       └── page.tsx
│   ├── dashboard/              # Protected routes
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── tasks/
│   │       └── page.tsx
│   └── api/                    # API routes (if needed)
│       └── auth/
│           └── route.ts
├── components/
│   ├── ui/                     # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── Modal.tsx
│   ├── tasks/                  # Task-specific components
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskFilters.tsx
│   └── layout/                 # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api.ts                  # API client for backend
│   ├── auth.ts                 # Better Auth configuration
│   ├── utils.ts                # Utility functions
│   └── types.ts                # TypeScript types
├── hooks/
│   ├── useTasks.ts             # Task data fetching
│   ├── useAuth.ts              # Authentication state
│   └── useChat.ts              # Chat functionality (Phase III)
├── public/
│   └── assets/                 # Static assets
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### 2. Root Layout

**app/layout.tsx:**
```tsx
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Evolution of Todo',
  description: 'Hackathon II - Spec-Driven Development',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50">
          {children}
        </div>
      </body>
    </html>
  )
}
```

**app/globals.css:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply text-gray-900 antialiased;
  }
}

@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors;
  }

  .btn-secondary {
    @apply px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors;
  }

  .input-field {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  }
}
```

### 3. API Client

**lib/api.ts:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  setToken(token: string) {
    this.token = token
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  // Task endpoints
  async getTasks(userId: string, status: string = 'all') {
    return this.request<Task[]>(`/api/${userId}/tasks?status=${status}`)
  }

  async getTask(userId: string, taskId: number) {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`)
  }

  async createTask(userId: string, task: TaskCreate) {
    return this.request<Task>(`/api/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(task),
    })
  }

  async updateTask(userId: string, taskId: number, task: TaskUpdate) {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(task),
    })
  }

  async deleteTask(userId: string, taskId: number) {
    await this.request(`/api/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    })
  }

  async toggleComplete(userId: string, taskId: number) {
    return this.request<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    })
  }

  // Chat endpoint (Phase III)
  async sendMessage(userId: string, message: string, conversationId?: number) {
    return this.request<ChatResponse>(`/api/${userId}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message, conversation_id: conversationId }),
    })
  }
}

export const api = new ApiClient(API_BASE_URL)

// Types
export interface Task {
  id: number
  user_id: string
  title: string
  description?: string
  completed: boolean
  priority?: 'high' | 'medium' | 'low'
  due_date?: string
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
  priority?: 'high' | 'medium' | 'low'
  due_date?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  priority?: 'high' | 'medium' | 'low'
  due_date?: string
  completed?: boolean
}

export interface ChatResponse {
  conversation_id: number
  response: string
  tool_calls: any[]
}
```

### 4. Authentication with Better Auth

**lib/auth.ts:**
```typescript
import { createAuthClient } from "better-auth/react"

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
})

export const { signIn, signUp, signOut, useSession } = authClient
```

**hooks/useAuth.ts:**
```typescript
'use client'

import { useSession } from '@/lib/auth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function useAuth(requireAuth: boolean = false) {
  const { data: session, isPending } = useSession()
  const router = useRouter()

  useEffect(() => {
    if (!isPending && requireAuth && !session) {
      router.push('/login')
    }
  }, [session, isPending, requireAuth, router])

  return { session, isPending, isAuthenticated: !!session }
}
```

**Middleware for protected routes (middleware.ts):**
```typescript
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Check for auth token in cookies
  const token = request.cookies.get('better-auth.session_token')

  // Protect /dashboard routes
  if (request.nextUrl.pathname.startsWith('/dashboard')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: '/dashboard/:path*',
}
```

### 5. Task Components

**components/tasks/TaskList.tsx (Client Component):**
```tsx
'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { Task } from '@/lib/api'
import TaskItem from './TaskItem'

interface TaskListProps {
  userId: string
  initialTasks?: Task[]
}

export default function TaskList({ userId, initialTasks = [] }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>(initialTasks)
  const [filter, setFilter] = useState<'all' | 'pending' | 'completed'>('all')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadTasks()
  }, [filter])

  const loadTasks = async () => {
    setLoading(true)
    try {
      const data = await api.getTasks(userId, filter)
      setTasks(data)
    } catch (error) {
      console.error('Failed to load tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (taskId: number) => {
    try {
      const updated = await api.toggleComplete(userId, taskId)
      setTasks(tasks.map(t => t.id === taskId ? updated : t))
    } catch (error) {
      console.error('Failed to toggle task:', error)
    }
  }

  const handleDelete = async (taskId: number) => {
    try {
      await api.deleteTask(userId, taskId)
      setTasks(tasks.filter(t => t.id !== taskId))
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }

  return (
    <div>
      {/* Filter buttons */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setFilter('all')}
          className={`px-4 py-2 rounded-lg ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          All
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={`px-4 py-2 rounded-lg ${filter === 'pending' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Pending
        </button>
        <button
          onClick={() => setFilter('completed')}
          className={`px-4 py-2 rounded-lg ${filter === 'completed' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          Completed
        </button>
      </div>

      {/* Task list */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="space-y-2">
          {tasks.map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </div>
  )
}
```

**components/tasks/TaskItem.tsx:**
```tsx
import type { Task } from '@/lib/api'

interface TaskItemProps {
  task: Task
  onToggle: (id: number) => void
  onDelete: (id: number) => void
}

export default function TaskItem({ task, onToggle, onDelete }: TaskItemProps) {
  return (
    <div className="flex items-center gap-4 p-4 bg-white rounded-lg shadow">
      <input
        type="checkbox"
        checked={task.completed}
        onChange={() => onToggle(task.id)}
        className="w-5 h-5"
      />
      <div className="flex-1">
        <h3 className={`font-medium ${task.completed ? 'line-through text-gray-500' : ''}`}>
          {task.title}
        </h3>
        {task.description && (
          <p className="text-sm text-gray-600">{task.description}</p>
        )}
        {task.priority && (
          <span className={`text-xs px-2 py-1 rounded ${
            task.priority === 'high' ? 'bg-red-100 text-red-800' :
            task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
            'bg-green-100 text-green-800'
          }`}>
            {task.priority}
          </span>
        )}
      </div>
      <button
        onClick={() => onDelete(task.id)}
        className="px-3 py-1 text-red-600 hover:bg-red-50 rounded"
      >
        Delete
      </button>
    </div>
  )
}
```

**components/tasks/TaskForm.tsx (Client Component):**
```tsx
'use client'

import { useState } from 'react'
import { api, type TaskCreate } from '@/lib/api'

interface TaskFormProps {
  userId: string
  onSuccess?: () => void
}

export default function TaskForm({ userId, onSuccess }: TaskFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [priority, setPriority] = useState<'high' | 'medium' | 'low'>('medium')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const task: TaskCreate = {
        title,
        description: description || undefined,
        priority,
      }
      await api.createTask(userId, task)
      setTitle('')
      setDescription('')
      setPriority('medium')
      onSuccess?.()
    } catch (error) {
      console.error('Failed to create task:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white rounded-lg shadow">
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          maxLength={200}
          className="input-field"
          placeholder="What needs to be done?"
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          maxLength={1000}
          rows={3}
          className="input-field"
          placeholder="Add more details..."
        />
      </div>

      <div>
        <label htmlFor="priority" className="block text-sm font-medium mb-1">
          Priority
        </label>
        <select
          id="priority"
          value={priority}
          onChange={(e) => setPriority(e.target.value as 'high' | 'medium' | 'low')}
          className="input-field"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading || !title}
        className="btn-primary w-full disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  )
}
```

### 6. Dashboard Page

**app/dashboard/page.tsx:**
```tsx
import { redirect } from 'next/navigation'
import TaskList from '@/components/tasks/TaskList'
import TaskForm from '@/components/tasks/TaskForm'

async function getSession() {
  // In real app, get session from Better Auth
  // For now, return mock session
  return { user: { id: 'user123', email: 'user@example.com' } }
}

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">My Tasks</h1>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Add New Task</h2>
          <TaskForm userId={session.user.id} />
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-4">Task List</h2>
          <TaskList userId={session.user.id} />
        </div>
      </div>
    </div>
  )
}
```

### 7. Login Page

**app/(auth)/login/page.tsx:**
```tsx
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { signIn } from '@/lib/auth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await signIn.email({ email, password })
      router.push('/dashboard')
    } catch (error) {
      console.error('Login failed:', error)
      alert('Login failed. Please check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-8 bg-white rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold text-center mb-6">Login</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="input-field"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="input-field"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <p className="text-center mt-4 text-sm text-gray-600">
          Don't have an account?{' '}
          <a href="/signup" className="text-blue-600 hover:underline">
            Sign up
          </a>
        </p>
      </div>
    </div>
  )
}
```

### 8. Custom Hooks

**hooks/useTasks.ts:**
```typescript
'use client'

import { useState, useEffect } from 'react'
import { api, type Task } from '@/lib/api'

export function useTasks(userId: string, filter: string = 'all') {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    loadTasks()
  }, [userId, filter])

  const loadTasks = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getTasks(userId, filter)
      setTasks(data)
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load tasks'))
    } finally {
      setLoading(false)
    }
  }

  const createTask = async (task: TaskCreate) => {
    const newTask = await api.createTask(userId, task)
    setTasks([...tasks, newTask])
    return newTask
  }

  const updateTask = async (taskId: number, updates: TaskUpdate) => {
    const updated = await api.updateTask(userId, taskId, updates)
    setTasks(tasks.map(t => t.id === taskId ? updated : t))
    return updated
  }

  const deleteTask = async (taskId: number) => {
    await api.deleteTask(userId, taskId)
    setTasks(tasks.filter(t => t.id !== taskId))
  }

  const toggleComplete = async (taskId: number) => {
    const updated = await api.toggleComplete(userId, taskId)
    setTasks(tasks.map(t => t.id === taskId ? updated : t))
    return updated
  }

  return {
    tasks,
    loading,
    error,
    loadTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  }
}
```

## Best Practices

### 1. Server vs Client Components
- ✅ Use Server Components by default (faster, smaller bundle)
- ✅ Use Client Components only when needed:
  - Interactive elements (buttons, forms)
  - Browser APIs (localStorage, etc.)
  - React hooks (useState, useEffect)
- ✅ Add `'use client'` directive at top of client component files

### 2. Data Fetching
- ✅ Fetch data in Server Components when possible
- ✅ Use React Query or SWR for client-side data fetching
- ✅ Implement loading and error states
- ✅ Cache and revalidate appropriately

### 3. Styling with Tailwind
- ✅ Use utility classes for rapid development
- ✅ Extract common patterns into custom classes or components
- ✅ Use Tailwind's responsive modifiers (`md:`, `lg:`, etc.)
- ✅ Configure theme in `tailwind.config.ts`

### 4. TypeScript
- ✅ Define types for all props and state
- ✅ Use interfaces for complex objects
- ✅ Leverage type inference when possible
- ✅ Avoid `any` type

### 5. Performance
- ✅ Use Next.js Image component for optimized images
- ✅ Implement code splitting and lazy loading
- ✅ Minimize client-side JavaScript
- ✅ Use Server Components for static content

## Environment Variables

**.env.local:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
BETTER_AUTH_SECRET=your-secret-key-here
```

## Dependencies

**package.json:**
```json
{
  "dependencies": {
    "next": "^16.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^1.0.0",
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

## Running the Application

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Integration with Hackathon Phases

### Phase II: Full-Stack Web App
- Implement all Basic Level features UI
- Integrate Better Auth for authentication
- Create responsive, accessible interface

### Phase III: AI Chatbot
- Add ChatKit React integration
- Create chat interface component
- Handle streaming responses

### Phase V: Advanced Features
- Add advanced filtering and sorting UI
- Implement due date pickers
- Create priority and tag management UI

## Summary

This skill provides a complete modern frontend implementation using Next.js App Router, optimized for performance, type safety, and developer experience. Follow SDD principles: specify UI requirements, plan component architecture, break into tasks, then implement with this skill.
