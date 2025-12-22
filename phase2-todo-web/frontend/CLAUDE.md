# Frontend Guidelines for `phase2-todo-web`

This document outlines the technical stack, architectural patterns, and UI/UX vision for the Next.js frontend of the Evolution-of-Todo application.

## 1. Core Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | Next.js (App Router) | React framework for server-side rendering and static site generation. |
| **Language** | TypeScript | For type safety and improved developer experience. |
| **Styling** | Tailwind CSS | A utility-first CSS framework for rapid UI development. |
| **Animation** | Framer Motion | For creating fluid and complex animations. |
| **Icons** | `lucide-react`, `react-icons` | For a comprehensive and consistent set of icons. |
| **State Management**| Zustand | Simple, fast, and scalable state management. |
| **Data Fetching** | React Query (TanStack Query) | For fetching, caching, and managing server state. |

---

## 2. Project Structure & Patterns

### Project Structure
```
/frontend
├── /app                  # App Router: pages, layouts, and API routes
│   ├── (auth)/           # Route group for authentication pages (e.g., /login)
│   ├── (dashboard)/      # Route group for protected dashboard pages
│   │   ├── /tasks/
│   │   ├── /settings/
│   │   └── layout.tsx    # Dashboard layout with sidebar
│   └── layout.tsx        # Root layout
├── /components           # Reusable UI components
│   ├── /ui/              # Generic, shadcn-like components (Button, Card, etc.)
│   ├── /layout/          # Layout components (Navbar, Footer, Sidebar)
│   └── /features/        # Components specific to a feature (e.g., TaskList)
├── /lib                  # Utility functions, API client, etc.
├── /hooks                # Custom React hooks
├── /store                # Zustand state management stores
└── /styles               # Global styles and Tailwind CSS base
```

### Key Architectural Patterns
- **Server Components by Default**: Utilize Next.js Server Components for fetching data and rendering static content to maximize performance.
- **Client Components for Interactivity**: Use the `'use client'` directive only for components that require state, effects, or browser-only APIs (e.g., forms, interactive charts).
- **Centralized API Client**: All backend communication should be handled through a centralized API client in `/lib/api.ts`, which uses React Query for hooks (`useTasks`, `useCreateTask`, etc.).
- **Atomic & Composable Components**: Build small, single-responsibility components in `/components/ui` and compose them into larger feature components.

---

## 3. Styling, Design System & UI/UX Vision

The application should feel modern, fluid, and visually engaging. The core aesthetic will be a combination of **glassmorphism** and **neon glows** that works seamlessly in both **light and dark modes**.

### Theming
The application must support both a light and a dark theme. The specific color palette should be chosen to maximize readability and visual appeal for the glassmorphism/neon aesthetic. A theme toggler should be accessible to the user, for example, in the settings or dashboard header.

### Responsiveness
A mobile-first approach is crucial. The layout should be fully responsive and adapt gracefully to all screen sizes using Tailwind CSS's standard breakpoints (`sm`, `md`, `lg`, `xl`).
- **Navigation**:
    - On desktop (`lg` and up), the main navbar will show all links.
    - On tablet and mobile (`md` and down), the navbar links will collapse into a hamburger menu.
- **Dashboard Sidebar**:
    - On desktop, the sidebar will be visible by default.
    - On smaller screens, it will be hidden by default and can be toggled open as a slide-over panel.
- **Grids**: All multi-column grids (e.g., Features section, Dashboard cards) must reflow into a single, vertical column on mobile screens (`sm`).
- **Task View**: The task list should adapt for smaller screens, potentially switching from a table-like view to a stacked card view to ensure all information is readable without horizontal scrolling.

### Icons
- Use `lucide-react` as the primary icon library for its clean, modern aesthetic.
- Use `react-icons` as a fallback if a specific icon is not available in Lucide.

### Animations
- **Provider**: Use Framer Motion's `motion` components and `AnimatePresence`.
- **Page Transitions**: Implement subtle fade-in/slide-up transitions on page load.
- **Micro-interactions**: Animate button clicks, hover effects, and modal pop-ups to feel responsive and satisfying.
- **Layout Animations**: Use `AnimatePresence` for lists (like the task list) to smoothly animate items being added or removed.

---

## 4. Key Pages & Components

### Landing Page
A visually stunning marketing page to attract users.
- **Navbar**:
  - Transparent/frosted glass effect, fully responsive.
  - Logo on the left.
  - "Login" and "Sign Up" buttons on the right (collapsing into a hamburger menu on mobile). The "Sign Up" button should be a primary CTA style.
- **Hero Section**:
  - Catchy headline: "Organize Your World, Evolve Your Workflow."
  - Sub-headline: "From simple lists to intelligent insights, the last todo app you'll ever need."
  - **CTA Button: "Create Your First Task"**:
    - If the user is logged in, it navigates to `/dashboard/tasks`.
    - If the user is logged out, it opens the Sign-Up modal.
- **Features Section**:
  - A responsive grid of 3-4 glassmorphism `Card` components.
  - Each card has an icon (`lucide-react`), a feature title (e.g., "Smart Prioritization"), and a brief description.
  - Cards should have a neon glow effect on hover.
- **Final CTA Section**:
  - A large, centered section with a headline like "Ready to Get Started?".
  - **CTA Button: "Start For Free"**: Opens the Sign-Up modal.
- **Footer**:
  - Simple, clean footer with links to social media, terms of service, and a copyright notice.

### Dashboard (`/dashboard`)
The main hub for authenticated users, with a responsive layout.
- **Sidebar**:
  - Collapsible and responsive as described in the Responsiveness section.
  - Navigation links with icons:
    - **Dashboard**: Overview and stats.
    - **Tasks**: The main task management view.
    - **Settings**: User profile and application settings.
  - User avatar and name at the bottom, with a logout button.
- **Main Content Area**:
  - A responsive grid of cards displaying various data visualizations:
    - **`TaskCompletionChart`**: A line or bar chart showing tasks completed over the last 7 days.
    - **`PriorityPieChart`**: A pie or donut chart showing the breakdown of tasks by priority (High, Medium, Low).
    - **`ActivityFeed`**: A list of recent activities (e.g., "You created 'Deploy to Vercel'").
    - **`ProgressOverview`**: A card with progress bars for different projects or task categories.

### Task Management View (`/dashboard/tasks`)
- **Header**:
  - "Tasks" title.
  - **Search Bar**: A prominent search bar with a `Search` icon.
  - **Filter Buttons**: Dropdown menus to filter by Status, Priority, and Tags.
  - **"New Task" Button**: Opens the create task modal.
- **Task List**:
  - A list of `TaskCard` components, animated with `AnimatePresence`, adapting to screen size.
- **`TaskCard` Component**:
  - Glassmorphism card with a subtle neon border color-coded by priority.
  - **Layout**:
    - **Left**: A checkbox to toggle completion status.
    - **Center**:
      - `Title` with a strikethrough when completed.
      - `Description`.
      - `Due Date` and `Creation Date` with a `Calendar` icon.
      - A row of `Tag` badges.
    - **Right**:
      - A `Priority` badge in the top-right corner.
      - "Edit" and "Delete" icon buttons that appear on hover.
      
### Modals (Create/Update Task, Signup/Login)
- All modals should appear with a scale/fade-in animation using Framer Motion.
- They should have a glassmorphism background with a blurred backdrop to focus the user's attention.
