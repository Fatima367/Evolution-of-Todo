# Chat Components

This directory contains the ChatKit-powered conversational interface components for the Todo AI Chatbot (Phase III).

## Overview

The chat components provide a natural language interface for managing todos through conversation with an AI assistant. The implementation uses OpenAI's ChatKit React library for a production-ready chat UI with built-in features like message rendering, streaming, and thread management.

## Components

### FloatingChatButton.tsx

A floating action button that opens a ChatKit-powered chat interface in a popup overlay.

**Features:**
- Positioned bottom-right of the viewport (responsive)
- Opens a 420x600px chat popup on click
- Integrates with ChatKit React for full chat functionality
- Persists conversation threads in localStorage
- Backdrop click-to-close functionality
- "New Chat" button to reset conversation
- Dark theme with neon blue accents (consistent with app design)

**ChatKit Configuration:**
- **Backend URL**: `http://localhost:8000/chatkit` (configurable via environment)
- **Domain Key**: `localhost` (required for local development)
- **Theme**: Dark mode with custom glassmorphism styling
- **Thread Persistence**: Automatic saving to localStorage
- **Start Screen**: Custom greeting and prompt suggestions

**Usage:**
```tsx
import { FloatingChatButton } from '@/components/chat'

export default function DashboardLayout() {
  return (
    <>
      {/* Your dashboard content */}
      <FloatingChatButton />
    </>
  )
}
```

## Architecture

### Backend Integration

The chat components communicate with the FastAPI backend via the ChatKit protocol:

**Endpoint**: `POST /chatkit`
**Request Format**: ChatKit `ThreadItem` format
**Response Format**: ChatKit `StreamingResult` with tool call information

### Conversation Persistence

- **Client-side**: Thread IDs stored in `localStorage` under key `chatkit-thread-id`
- **Server-side**: Full conversation history in PostgreSQL (`conversations` and `messages` tables)
- **Stateless Server**: Each request is self-contained; server doesn't maintain session state

### Tool Integration

The backend ChatKit server exposes MCP (Model Context Protocol) tools for task operations:
- `add_task` - Create new task
- `list_tasks` - List tasks with filters
- `complete_task` - Mark task as complete
- `update_task` - Update task details
- `delete_task` - Remove task

Tool calls are executed automatically by the AI agent based on natural language understanding.

## Styling

The chat interface follows the application's design system:

**Theme**: Dark glassmorphism with neon blue accents
**Colors**:
- Background: `#16213e` (dark blue-gray)
- Accent: `#4cc9f0` (neon cyan)
- Secondary: `#4361ee` (electric blue)
- Overlay: `#0f3460` (darker blue)

**Effects**:
- Glassmorphism cards with backdrop blur
- Neon glow on interactive elements
- Smooth entrance animations (scale + fade)
- Responsive sizing for mobile devices

## Environment Variables

```env
NEXT_PUBLIC_CHATKIT_BACKEND_URL=http://localhost:8000/chatkit
```

## Testing

The chat components are designed to work with the backend test suite:

**Contract Tests**: `backend/tests/contract/` - Validates ChatKit protocol compliance
**Integration Tests**: `backend/tests/integration/` - Tests tool execution and conversation flow
**E2E Tests**: `frontend/tests/e2e/` - Tests full user interaction flows

## Dependencies

```json
{
  "@openai/chatkit-react": "^1.3.0",
  "react": "^18.3.1",
  "react-dom": "^18.3.1"
}
```

## Related Documentation

- [ChatKit Official Docs](https://platform.openai.com/docs/chatkit)
- [Backend ChatKit Server](../../../backend/src/chatkit/README.md)
- [MCP Tools Documentation](../../../specs/003-todo-ai-chatbot/contracts/mcp-tools.yaml)
- [Chat API Specification](../../../specs/003-todo-ai-chatbot/contracts/chat-api.yaml)

## Production Deployment Notes

### Fix for Blank Screen Issue

The ChatKit component was showing a blank screen in production due to SSR/hydration mismatches. The issue was resolved by:

1. Adding proper checks for `window` and `document` objects before accessing them
2. Implementing a Next.js API route proxy at `/api/chatkit` to handle requests in production
3. Using conditional logic to switch between direct backend calls (development) and API routes (production)

### Environment Configuration

For production deployment, ensure the following environment variables are set:

```env
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
NEXT_PUBLIC_BASE_URL=https://your-frontend-domain.com
```

### API Route Proxy

The `/api/chatkit` route acts as a proxy between the frontend and backend services, handling:
- Authentication token forwarding
- Request/response transformation
- CORS handling
- Streaming response management

## Future Enhancements

- Multi-layout support (fullpage, sidebar, popup-left)
- Custom theme switcher (light/dark mode toggle)
- Message export functionality
- Conversation history browser
- Voice input integration (Phase IV)
- Urdu language support (Phase IV)
