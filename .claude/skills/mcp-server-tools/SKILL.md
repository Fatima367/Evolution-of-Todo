---
name: MCP Server Tools Development Skill
description: Expert skill for building Model Context Protocol (MCP) servers with tool definitions for AI agents. Specializes in Official MCP SDK for Python, tool schema design, and integration with OpenAI Agents SDK.
tags: [mcp, model-context-protocol, ai-tools, openai-agents, python, phase-iii]
---

# MCP Server Tools Development Skill

## Overview

This skill provides expertise in building MCP servers for Phase III of the hackathon:
- **Official MCP SDK** (Python) - Model Context Protocol implementation
- **Tool definitions** - Create tools for AI agents to manage tasks
- **OpenAI Agents SDK** integration - Connect MCP tools to AI agents
- **Stateless design** - Tools that store state in database, not memory

**Phase III Requirement:**
Build an MCP server with tools (add_task, list_tasks, update_task, delete_task, complete_task) that the AI chatbot uses to manage todos via natural language.

## Core Concepts

### What is MCP?

**Model Context Protocol (MCP)** is a standardized interface for AI applications to interact with external services through **tools**. Instead of the AI directly calling your API, it calls MCP tools, which then execute the operations.

### Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │ OpenAI Agents SDK │     │             │     │             │
│  ChatKit    │────▶│   + Agent Runner  │────▶│ MCP Server  │────▶│  Neon DB    │
│  Frontend   │     │                   │     │  (Tools)    │     │             │
│             │     └──────────────────┘     └─────────────┘     └─────────────┘
└─────────────┘              │
                             │
                             ▼
                    ┌──────────────────┐
                    │  Tool Calls:     │
                    │  - add_task      │
                    │  - list_tasks    │
                    │  - update_task   │
                    │  - delete_task   │
                    │  - complete_task │
                    └──────────────────┘
```

### Why Use MCP?

| Without MCP | With MCP |
|-------------|----------|
| AI calls REST API directly | AI calls standardized MCP tools |
| Custom integration per AI provider | Works with any MCP-compatible agent |
| Manual prompt engineering for API calls | Automatic tool discovery and validation |
| Error handling in prompts | Structured error responses |

## Installation

```bash
# Install Official MCP SDK
pip install mcp

# Install OpenAI Agents SDK with MCP support
pip install openai-agents
```

## MCP Server Structure

**File Organization:**
```
backend/
├── main.py                    # FastAPI app
├── mcp_server.py              # MCP server definition
├── mcp_tools/
│   ├── __init__.py
│   ├── task_tools.py          # Task management tools
│   └── schemas.py             # Tool input/output schemas
├── models.py                  # SQLModel database models
└── db.py                      # Database connection
```

## Building MCP Tools

### 1. Tool Schema Definitions

**mcp_tools/schemas.py:**
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class AddTaskInput(BaseModel):
    """Input schema for adding a new task"""
    user_id: str = Field(..., description="ID of the user creating the task")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[str] = Field("medium", pattern="^(high|medium|low)$", description="Task priority")

class AddTaskOutput(BaseModel):
    """Output schema for add_task"""
    task_id: int
    status: str
    title: str

class ListTasksInput(BaseModel):
    """Input schema for listing tasks"""
    user_id: str = Field(..., description="ID of the user")
    status: Optional[str] = Field("all", pattern="^(all|pending|completed)$", description="Filter by status")

class TaskData(BaseModel):
    """Task data structure"""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: Optional[str]
    created_at: datetime

class ListTasksOutput(BaseModel):
    """Output schema for list_tasks"""
    tasks: List[TaskData]
    count: int

class CompleteTaskInput(BaseModel):
    """Input schema for marking task complete"""
    user_id: str = Field(..., description="ID of the user")
    task_id: int = Field(..., description="ID of the task to complete")

class CompleteTaskOutput(BaseModel):
    """Output schema for complete_task"""
    task_id: int
    status: str
    title: str

class DeleteTaskInput(BaseModel):
    """Input schema for deleting a task"""
    user_id: str = Field(..., description="ID of the user")
    task_id: int = Field(..., description="ID of the task to delete")

class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task"""
    task_id: int
    status: str
    title: str

class UpdateTaskInput(BaseModel):
    """Input schema for updating a task"""
    user_id: str = Field(..., description="ID of the user")
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[str] = Field(None, pattern="^(high|medium|low)$")

class UpdateTaskOutput(BaseModel):
    """Output schema for update_task"""
    task_id: int
    status: str
    title: str
```

### 2. MCP Tool Implementations

**mcp_tools/task_tools.py:**
```python
from mcp import Tool
from sqlmodel import Session, select
from models import Task
from db import get_session
from mcp_tools.schemas import (
    AddTaskInput, AddTaskOutput,
    ListTasksInput, ListTasksOutput, TaskData,
    CompleteTaskInput, CompleteTaskOutput,
    DeleteTaskInput, DeleteTaskOutput,
    UpdateTaskInput, UpdateTaskOutput
)
from datetime import datetime

class AddTaskTool(Tool):
    """Tool for creating a new task"""

    name = "add_task"
    description = "Create a new task in the todo list"
    input_schema = AddTaskInput
    output_schema = AddTaskOutput

    async def run(self, input_data: AddTaskInput) -> AddTaskOutput:
        """Execute the add_task operation"""
        with next(get_session()) as session:
            # Create new task
            task = Task(
                user_id=input_data.user_id,
                title=input_data.title,
                description=input_data.description,
                priority=input_data.priority,
                completed=False,
            )

            session.add(task)
            session.commit()
            session.refresh(task)

            return AddTaskOutput(
                task_id=task.id,
                status="created",
                title=task.title
            )


class ListTasksTool(Tool):
    """Tool for retrieving tasks from the list"""

    name = "list_tasks"
    description = "Retrieve tasks from the todo list with optional filtering"
    input_schema = ListTasksInput
    output_schema = ListTasksOutput

    async def run(self, input_data: ListTasksInput) -> ListTasksOutput:
        """Execute the list_tasks operation"""
        with next(get_session()) as session:
            # Build query
            query = select(Task).where(Task.user_id == input_data.user_id)

            # Apply status filter
            if input_data.status == "pending":
                query = query.where(Task.completed == False)
            elif input_data.status == "completed":
                query = query.where(Task.completed == True)

            # Execute query
            tasks = session.exec(query).all()

            # Convert to output format
            task_data = [
                TaskData(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    completed=task.completed,
                    priority=task.priority,
                    created_at=task.created_at
                )
                for task in tasks
            ]

            return ListTasksOutput(
                tasks=task_data,
                count=len(task_data)
            )


class CompleteTaskTool(Tool):
    """Tool for marking a task as complete"""

    name = "complete_task"
    description = "Mark a task as complete"
    input_schema = CompleteTaskInput
    output_schema = CompleteTaskOutput

    async def run(self, input_data: CompleteTaskInput) -> CompleteTaskOutput:
        """Execute the complete_task operation"""
        with next(get_session()) as session:
            # Get task
            task = session.get(Task, input_data.task_id)

            if not task or task.user_id != input_data.user_id:
                raise ValueError(f"Task {input_data.task_id} not found")

            # Mark as complete
            task.completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return CompleteTaskOutput(
                task_id=task.id,
                status="completed",
                title=task.title
            )


class DeleteTaskTool(Tool):
    """Tool for removing a task from the list"""

    name = "delete_task"
    description = "Remove a task from the todo list"
    input_schema = DeleteTaskInput
    output_schema = DeleteTaskOutput

    async def run(self, input_data: DeleteTaskInput) -> DeleteTaskOutput:
        """Execute the delete_task operation"""
        with next(get_session()) as session:
            # Get task
            task = session.get(Task, input_data.task_id)

            if not task or task.user_id != input_data.user_id:
                raise ValueError(f"Task {input_data.task_id} not found")

            # Store title before deletion
            task_title = task.title
            task_id = task.id

            # Delete task
            session.delete(task)
            session.commit()

            return DeleteTaskOutput(
                task_id=task_id,
                status="deleted",
                title=task_title
            )


class UpdateTaskTool(Tool):
    """Tool for modifying task title or description"""

    name = "update_task"
    description = "Modify task title, description, or priority"
    input_schema = UpdateTaskInput
    output_schema = UpdateTaskOutput

    async def run(self, input_data: UpdateTaskInput) -> UpdateTaskOutput:
        """Execute the update_task operation"""
        with next(get_session()) as session:
            # Get task
            task = session.get(Task, input_data.task_id)

            if not task or task.user_id != input_data.user_id:
                raise ValueError(f"Task {input_data.task_id} not found")

            # Update fields if provided
            if input_data.title is not None:
                task.title = input_data.title
            if input_data.description is not None:
                task.description = input_data.description
            if input_data.priority is not None:
                task.priority = input_data.priority

            task.updated_at = datetime.utcnow()

            session.add(task)
            session.commit()
            session.refresh(task)

            return UpdateTaskOutput(
                task_id=task.id,
                status="updated",
                title=task.title
            )
```

### 3. MCP Server Setup

**mcp_server.py:**
```python
from mcp import MCPServer
from mcp_tools.task_tools import (
    AddTaskTool,
    ListTasksTool,
    CompleteTaskTool,
    DeleteTaskTool,
    UpdateTaskTool
)

# Create MCP server
mcp_server = MCPServer(
    name="todo-mcp-server",
    version="1.0.0",
    description="MCP server for Todo task management"
)

# Register tools
mcp_server.add_tool(AddTaskTool())
mcp_server.add_tool(ListTasksTool())
mcp_server.add_tool(CompleteTaskTool())
mcp_server.add_tool(DeleteTaskTool())
mcp_server.add_tool(UpdateTaskTool())

# Tool list for easy access
TOOLS = [
    AddTaskTool(),
    ListTasksTool(),
    CompleteTaskTool(),
    DeleteTaskTool(),
    UpdateTaskTool(),
]
```

## Integration with OpenAI Agents SDK

### Chat Endpoint with MCP Tools

**routes/chat.py:**
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from typing import Optional
from agents import Agent, Runner
from models import Conversation, Message
from db import get_session
from dependencies import get_current_user
from mcp_server import TOOLS

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    tool_calls: list = []

# Create AI agent with MCP tools
agent = Agent(
    name="Todo Assistant",
    instructions="""You are a helpful todo list assistant. You help users manage their tasks
    using natural language. You can add tasks, list tasks, mark tasks complete, delete tasks,
    and update tasks. Always confirm actions with the user and provide friendly responses.""",
    tools=TOOLS,  # MCP tools
    model="gpt-4o",  # or use LiteLLM for Gemini
)

@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Handle chat messages with AI agent using MCP tools"""
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get or create conversation
    if request.conversation_id:
        conversation = session.get(Conversation, request.conversation_id)
        if not conversation or conversation.user_id != user_id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Store user message
    user_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="user",
        content=request.message
    )
    session.add(user_message)
    session.commit()

    # Load conversation history
    messages_query = select(Message).where(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at)
    history = session.exec(messages_query).all()

    # Build messages for agent
    agent_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in history
    ]

    # Run agent with MCP tools
    # The agent will automatically call MCP tools as needed
    result = Runner.run_sync(
        agent=agent,
        input=agent_messages,
        context={"user_id": user_id}  # Pass user_id to tools
    )

    # Extract response
    assistant_response = result.messages[-1].content if result.messages else "I couldn't process that."
    tool_calls = [
        {
            "tool": call.tool_name,
            "input": call.input,
            "output": call.output
        }
        for call in result.tool_calls
    ]

    # Store assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        user_id=user_id,
        role="assistant",
        content=assistant_response
    )
    session.add(assistant_message)
    session.commit()

    return ChatResponse(
        conversation_id=conversation.id,
        response=assistant_response,
        tool_calls=tool_calls
    )
```

## Natural Language Command Examples

The AI agent will understand these natural language commands and call the appropriate MCP tools:

| User Says | MCP Tool Called | Parameters |
|-----------|-----------------|------------|
| "Add a task to buy groceries" | `add_task` | title="Buy groceries" |
| "Show me all my tasks" | `list_tasks` | status="all" |
| "What's pending?" | `list_tasks` | status="pending" |
| "Mark task 3 as complete" | `complete_task` | task_id=3 |
| "Delete the meeting task" | First `list_tasks`, then `delete_task` | - |
| "Change task 1 to 'Call mom tonight'" | `update_task` | task_id=1, title="Call mom tonight" |
| "I need to remember to pay bills" | `add_task` | title="Pay bills" |
| "What have I completed?" | `list_tasks` | status="completed" |

## Agent Instructions for Better Performance

**Enhanced Agent Instructions:**
```python
agent = Agent(
    name="Todo Assistant",
    instructions="""You are a helpful and friendly todo list assistant.

Your capabilities:
1. Add tasks: When users mention needing to do something, add it as a task
2. List tasks: Show all tasks, or filter by pending/completed
3. Complete tasks: Mark tasks as done when users say they finished something
4. Delete tasks: Remove tasks users no longer need
5. Update tasks: Modify task titles, descriptions, or priorities

Guidelines:
- Always confirm when you perform an action (e.g., "I've added 'Buy groceries' to your list")
- If a user's request is ambiguous, ask for clarification
- When listing tasks, format them nicely and mention completion status
- If a task ID is mentioned, use it directly; otherwise, search by title
- Be conversational and helpful, not robotic

Example interactions:
- User: "Add buy milk to my list"
  You: "I've added 'Buy milk' to your todo list."

- User: "What do I need to do?"
  You: "Here are your pending tasks: [list tasks]. You have X tasks to complete."

- User: "I finished the report"
  You: "Great! I've marked 'Report' as complete. Anything else?"
""",
    tools=TOOLS,
    model="gpt-4o",
)
```

## Error Handling

**Tool Error Responses:**
```python
class CompleteTaskTool(Tool):
    async def run(self, input_data: CompleteTaskInput) -> CompleteTaskOutput:
        try:
            with next(get_session()) as session:
                task = session.get(Task, input_data.task_id)

                if not task:
                    raise ValueError(f"Task with ID {input_data.task_id} not found")

                if task.user_id != input_data.user_id:
                    raise ValueError(f"Task {input_data.task_id} does not belong to user {input_data.user_id}")

                task.completed = True
                task.updated_at = datetime.utcnow()

                session.add(task)
                session.commit()
                session.refresh(task)

                return CompleteTaskOutput(
                    task_id=task.id,
                    status="completed",
                    title=task.title
                )

        except ValueError as e:
            # Return error as part of output
            return CompleteTaskOutput(
                task_id=input_data.task_id,
                status="error",
                title=str(e)
            )
```

## Testing MCP Tools

**Direct Tool Testing:**
```python
# test_mcp_tools.py
from mcp_tools.task_tools import AddTaskTool, ListTasksTool
from mcp_tools.schemas import AddTaskInput, ListTasksInput

async def test_add_task():
    tool = AddTaskTool()
    input_data = AddTaskInput(
        user_id="user123",
        title="Test task",
        description="This is a test",
        priority="high"
    )
    result = await tool.run(input_data)
    print(f"Added task: {result.task_id} - {result.title}")

async def test_list_tasks():
    tool = ListTasksTool()
    input_data = ListTasksInput(user_id="user123", status="all")
    result = await tool.run(input_data)
    print(f"Found {result.count} tasks")
    for task in result.tasks:
        print(f"  - {task.title} (completed: {task.completed})")

# Run tests
import asyncio
asyncio.run(test_add_task())
asyncio.run(test_list_tasks())
```

## Best Practices

### 1. Stateless Tools
- ✅ Store all state in database, not in tool instances
- ✅ Use session management for database access
- ✅ Pass user_id to every tool for proper isolation

### 2. Schema Design
- ✅ Use Pydantic models for type safety
- ✅ Add clear descriptions to all fields
- ✅ Validate inputs with regex patterns where appropriate
- ✅ Return structured outputs, not just strings

### 3. Error Handling
- ✅ Handle missing tasks gracefully
- ✅ Verify user ownership before operations
- ✅ Return meaningful error messages
- ✅ Don't expose internal errors to users

### 4. Tool Naming
- ✅ Use clear, action-oriented names (add_task, not create)
- ✅ Be consistent (complete_task vs mark_complete)
- ✅ Match user mental model (not technical jargon)

### 5. Agent Instructions
- ✅ Provide clear capabilities list
- ✅ Include example interactions
- ✅ Set expectations for when to ask for clarification
- ✅ Define tone and personality

## Integration with Hackathon Requirements

### Phase III Deliverables
- ✅ MCP server with 5 required tools
- ✅ Integration with OpenAI Agents SDK
- ✅ Stateless design (database persistence)
- ✅ Natural language interface
- ✅ Conversation history support

### Tool Requirements Met
| Required Tool | Implementation | Status |
|---------------|----------------|--------|
| add_task | AddTaskTool | ✅ Complete |
| list_tasks | ListTasksTool | ✅ Complete |
| complete_task | CompleteTaskTool | ✅ Complete |
| delete_task | DeleteTaskTool | ✅ Complete |
| update_task | UpdateTaskTool | ✅ Complete |

## Summary

This skill provides complete MCP server implementation for Phase III, enabling AI-powered natural language task management. The tools are stateless, database-backed, and integrate seamlessly with OpenAI Agents SDK and ChatKit frontend.

**Key Benefits:**
- Standardized interface for AI tools
- Type-safe with Pydantic schemas
- Database-backed (stateless server)
- Works with any MCP-compatible AI agent
- Clear separation between tool logic and agent behavior
