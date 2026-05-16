"""ChatKit server implementation with Groq LLM and MCP tools

This module implements the ChatKit server with:
- Groq LLM provider via LiteLLM
- PostgreSQL-backed conversation storage
- MCP tools for task management
- ID collision fix for LiteLLM providers
"""
import os
from typing import AsyncIterator

from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel

from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import (
    ThreadMetadata, ThreadItem,
    ThreadItemAddedEvent, ThreadItemDoneEvent, ThreadItemUpdatedEvent,
    AssistantMessageItem
)
from chatkit.agents import AgentContext, stream_agent_response, ThreadItemConverter

# Import these at module level to avoid circular imports
# Store imports models, so we delay the import
from src.todo_chatkit.tools import create_task_tools, TaskToolContext
from src.todo_chatkit.store import PostgreSQLStore, ChatContext


class TodoChatKitServer(ChatKitServer[ChatContext]):
    """ChatKit server for Todo AI Chatbot

    Features:
    - Groq LLM via LiteLLM
    - PostgreSQL conversation persistence
    - MCP tools for task management
    - Full conversation history support
    - ID collision fix for non-OpenAI providers
    """

    def __init__(self, store):
        """Initialize TodoChatKitServer with PostgreSQL store

        Args:
            store: PostgreSQLStore instance for conversation persistence
        """
        super().__init__(store)
        self.converter = ThreadItemConverter()

        # Configure Groq model via LiteLLM
        groq_api_key = os.getenv("GROQ_API_KEY")
        groq_model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")

        self.model = LitellmModel(
            model=f"groq/{groq_model}",
            api_key=groq_api_key,
        )

    def create_agent(self, context, thread_id: str = "") -> Agent[AgentContext]:
        """Create AI agent with tools for the user

        Args:
            context: User context with session
            thread_id: Current conversation thread ID

        Returns:
            Configured Agent with task management tools
        """
        # Create user-specific tools with session, user_id, and thread_id
        tools = create_task_tools(context.session, context.user_id, thread_id)

        # Create agent with instructions
        agent = Agent[AgentContext](
            name="Todo Assistant",
            instructions="""You are a helpful todo assistant. Help users manage their tasks using the provided tools.

Available tools:
- add_task: Create a new task (requires title, optionally description and priority)
- list_tasks: Show tasks with optional status filter (pending/in_progress/completed/all). Supports searching by title.
- complete_task: Mark a task as completed using its ID or Title.
- delete_task: Remove a task using its ID or Title.
- update_task: Change task title, description, priority, or status using ID or Title.
- bulk_complete: Mark ALL your pending or in-progress tasks as completed.
- bulk_delete: Delete ALL your completed tasks.
- clear_all: Delete ALL your tasks (irreversible).

Behavior guidelines:
- Always confirm actions with a friendly response
- When listing tasks, present them in a clear, organized format (Markdown tables or lists)
- If a user refers to a task by name instead of ID and there are multiple matches, list the options clearly (e.g., "I found multiple tasks with that name, which one did you mean?") and provide the titles and IDs.
- For destructive bulk actions like 'clear_all', ALWAYS ask the user for confirmation first (e.g., "Are you sure you want to delete ALL your tasks? This cannot be undone.") before calling the tool.
- If a tool returns an 'ambiguous' status with matches, present those matches to the user and ask them to specify.
- Handle errors gracefully with helpful suggestions
- Be concise but helpful
- Use natural, conversational language
""",
            model=self.model,
            tools=tools,
        )

        return agent

    async def respond(
        self,
        thread: ThreadMetadata,
        input: ThreadItem,
        context: ChatContext
    ):
        """Process user input and generate AI response with streaming

        This method:
        1. Loads conversation history from PostgreSQL
        2. Converts history to agent input format
        3. Runs the AI agent with tools
        4. Applies ID collision fix for LiteLLM
        5. Streams response back to client

        Args:
            thread: Thread metadata
            input: User's message
            context: User context with session and user_id

        Yields:
            StreamingResult events
        """
        # Load full conversation history
        page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=100,  # Load last 100 messages
            order="asc",
            context=context
        )

        # Build message history including current input
        all_items = list(page.data)
        if input:
            all_items.append(input)

        # Convert to agent input format
        agent_input = await self.converter.to_agent_input(all_items)

        # Create tool context with session, user_id, and thread_id
        tool_context = TaskToolContext(
            session=context.session,
            user_id=str(context.user_id),
            thread_id=thread.id
        )

        # Create agent with tools
        agent = self.create_agent(context, thread.id)

        # Create agent context with proper request_context for tools
        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=tool_context
        )

        # Run agent with streaming
        result = Runner.run_streamed(agent, agent_input, context=agent_context)

        # Process events with ID collision fix
        async for event in self._process_agent_events(agent_context, result, thread, context):
            yield event

    async def _process_agent_events(
        self,
        agent_context: AgentContext,
        result,
        thread: ThreadMetadata,
        context: ChatContext
    ):
        """Process streaming events and fix LiteLLM/Groq ID collisions."""
        id_mapping: dict[str, str] = {}
        async for event in stream_agent_response(agent_context, result):
            if event.type == "thread.item.added" and isinstance(event.item, AssistantMessageItem):
                old_id = event.item.id
                if old_id not in id_mapping:
                    id_mapping[old_id] = self.store.generate_item_id("message", thread, context)
                event.item = event.item.model_copy(update={"id": id_mapping[old_id]})
            elif event.type == "thread.item.done" and isinstance(event.item, AssistantMessageItem):
                old_id = event.item.id
                if old_id in id_mapping:
                    event.item = event.item.model_copy(update={"id": id_mapping[old_id]})
            elif event.type == "thread.item.updated" and event.item_id in id_mapping:
                event = event.model_copy(update={"item_id": id_mapping[event.item_id]})
            yield event
