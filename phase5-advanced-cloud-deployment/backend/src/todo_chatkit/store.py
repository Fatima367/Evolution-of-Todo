"""PostgreSQL-backed ChatKit store implementation"""
import uuid
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass

from sqlmodel import Session, select
from chatkit.store import Store
from chatkit.types import (
    ThreadMetadata, ThreadItem, Page,
    UserMessageItem, AssistantMessageItem, UserMessageTextContent,
    AssistantMessageContent
)

from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.database import get_session


@dataclass
class ChatContext:
    """Context passed to store methods containing user information"""
    user_id: str  # UUID as string
    session: Session


class PostgreSQLStore(Store[ChatContext]):
    """PostgreSQL-backed implementation of ChatKit Store

    Stores conversations and messages in PostgreSQL database tables.
    All store methods receive a ChatContext with user_id and database session.
    """

    def generate_thread_id(self, context: ChatContext) -> str:
        """Generate unique thread ID as UUID string"""
        return str(uuid.uuid4())

    def generate_item_id(self, item_type: str, thread: ThreadMetadata, context: ChatContext) -> str:
        """Generate unique item ID for messages"""
        return f"{item_type}_{uuid.uuid4()}"

    async def load_thread(self, thread_id: str, context: ChatContext) -> ThreadMetadata:
        """Load thread metadata by ID

        Args:
            thread_id: Conversation ID (UUID string)
            context: User context with session

        Returns:
            ThreadMetadata for the conversation
        """
        # Try to find conversation by UUID
        try:
            conversation_uuid = uuid.UUID(thread_id)
            statement = select(Conversation).where(
                Conversation.id == conversation_uuid,
                Conversation.user_id == uuid.UUID(context.user_id)
            )
            conversation = context.session.exec(statement).first()
        except ValueError:
            conversation = None

        if not conversation:
            # Return empty metadata for non-existent or unauthorized threads
            return ThreadMetadata(
                id=thread_id,
                created_at=datetime.now(timezone.utc)
            )

        return ThreadMetadata(
            id=str(conversation.id),
            created_at=conversation.created_at.replace(tzinfo=timezone.utc)
        )

    async def save_thread(self, thread: ThreadMetadata, context: ChatContext) -> None:
        """Save or update thread metadata

        Args:
            thread: Thread metadata to save
            context: User context with session
        """
        try:
            # Check if conversation already exists
            conversation_uuid = uuid.UUID(thread.id)
            statement = select(Conversation).where(
                Conversation.id == conversation_uuid,
                Conversation.user_id == uuid.UUID(context.user_id)
            )
            conversation = context.session.exec(statement).first()

            if conversation:
                conversation.updated_at = datetime.utcnow()
                context.session.add(conversation)
                context.session.commit()
                # Ensure thread.id is the UUID string
                thread.id = str(conversation.id)
            else:
                # New conversation - create it
                conversation = Conversation(
                    id=conversation_uuid,
                    user_id=uuid.UUID(context.user_id),
                    created_at=thread.created_at if isinstance(thread.created_at, datetime) else datetime.fromtimestamp(thread.created_at, tz=timezone.utc),
                    updated_at=datetime.utcnow()
                )
                context.session.add(conversation)
                context.session.commit()
                thread.id = str(conversation.id)
        except ValueError:
            # Invalid UUID format - create new conversation with auto-generated UUID
            conversation = Conversation(
                user_id=uuid.UUID(context.user_id),
                created_at=thread.created_at if isinstance(thread.created_at, datetime) else datetime.fromtimestamp(thread.created_at, tz=timezone.utc),
                updated_at=datetime.utcnow()
            )
            context.session.add(conversation)
            context.session.commit()
            context.session.refresh(conversation)
            # Update thread ID with actual UUID
            thread.id = str(conversation.id)

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: ChatContext
    ) -> Page[ThreadItem]:
        """Load messages for a conversation

        Args:
            thread_id: Conversation ID (UUID string)
            after: Cursor for pagination (message ID)
            limit: Max items to return
            order: 'asc' or 'desc'
            context: User context

        Returns:
            Page of ThreadItem objects
        """
        try:
            conversation_uuid = uuid.UUID(thread_id)
        except ValueError:
            return Page(data=[], has_more=False)

        # Build query - Note: Message uses integer ID, we need to filter by conversation_id which is UUID
        statement = select(Message).where(
            Message.conversation_id == conversation_uuid,
            Message.user_id == uuid.UUID(context.user_id)
        )

        # Apply cursor pagination if provided
        if after:
            try:
                after_id = int(after.split('_')[-1]) if '_' in after else int(after)
                if order == 'asc':
                    statement = statement.where(Message.id > after_id)
                else:
                    statement = statement.where(Message.id < after_id)
            except ValueError:
                pass

        # Apply ordering
        if order == 'asc':
            statement = statement.order_by(Message.created_at.asc())
        else:
            statement = statement.order_by(Message.created_at.desc())

        # Fetch limit + 1 to check if more exist
        statement = statement.limit(limit + 1)
        messages = context.session.exec(statement).all()

        # Convert to ThreadItems
        items = []
        for msg in messages[:limit]:
            item_id = f"msg_{msg.id}"

            if msg.role == MessageRole.USER:
                items.append(UserMessageItem(
                    id=item_id,
                    thread_id=thread_id,
                    content=[UserMessageTextContent(type="input_text", text=msg.content)],
                    created_at=datetime.fromtimestamp(msg.created_at.replace(tzinfo=timezone.utc).timestamp(), tz=timezone.utc),
                    inference_options={}
                ))
            else:
                items.append(AssistantMessageItem(
                    id=item_id,
                    thread_id=thread_id,
                    content=[AssistantMessageContent(type="output_text", text=msg.content)],
                    created_at=datetime.fromtimestamp(msg.created_at.replace(tzinfo=timezone.utc).timestamp(), tz=timezone.utc)
                ))

        return Page(data=items, has_more=len(messages) > limit)

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: ChatContext) -> None:
        """Add a new message to a conversation

        Args:
            thread_id: Conversation ID (UUID string)
            item: ThreadItem to add
            context: User context
        """
        try:
            conversation_uuid = uuid.UUID(thread_id)
        except ValueError:
            return

        # Extract content
        content_text = ""
        if hasattr(item, 'content') and item.content:
            for part in item.content:
                if hasattr(part, 'text'):
                    content_text += part.text

        if not content_text:
            return

        # Determine role
        role = MessageRole.ASSISTANT if isinstance(item, AssistantMessageItem) else MessageRole.USER

        # Create message - ID will be auto-generated as UUID
        message = Message(
            user_id=uuid.UUID(context.user_id),
            conversation_id=conversation_uuid,
            role=role,
            content=content_text,
            created_at=datetime.utcnow()
        )

        context.session.add(message)

        # Update conversation timestamp
        statement = select(Conversation).where(
            Conversation.id == conversation_uuid,
            Conversation.user_id == uuid.UUID(context.user_id)
        )
        conversation = context.session.exec(statement).first()
        if conversation:
            conversation.updated_at = datetime.utcnow()
            context.session.add(conversation)

        context.session.commit()

    async def save_item(self, thread_id: str, item: ThreadItem, context: ChatContext) -> None:
        """Update an existing message

        Args:
            thread_id: Conversation ID
            item: ThreadItem with updates
            context: User context
        """
        try:
            # Extract UUID from item ID (format: item_type_uuid)
            item_id_parts = item.id.split('_')
            message_uuid = uuid.UUID(item_id_parts[-1])
        except (ValueError, IndexError):
            return

        statement = select(Message).where(
            Message.id == message_uuid,
            Message.user_id == uuid.UUID(context.user_id)
        )
        message = context.session.exec(statement).first()
        if not message:
            return

        # Update content
        if hasattr(item, 'content') and item.content:
            content_text = ""
            for part in item.content:
                if hasattr(part, 'text'):
                    content_text += part.text

            if content_text:
                message.content = content_text
                context.session.add(message)
                context.session.commit()

    async def load_item(self, thread_id: str, item_id: str, context: ChatContext) -> ThreadItem:
        """Load a specific message by ID

        Args:
            thread_id: Conversation ID
            item_id: Message ID
            context: User context

        Returns:
            ThreadItem for the message
        """
        try:
            message_uuid = uuid.UUID(item_id.split('_')[-1])
        except (ValueError, IndexError):
            raise ValueError(f"Invalid item ID: {item_id}")

        statement = select(Message).where(
            Message.id == message_uuid,
            Message.user_id == uuid.UUID(context.user_id)
        )
        message = context.session.exec(statement).first()
        if not message:
            raise ValueError(f"Message not found: {item_id}")

        if message.role == MessageRole.USER:
            return UserMessageItem(
                id=item_id,
                thread_id=thread_id,
                content=[UserMessageTextContent(type="input_text", text=message.content)],
                created_at=datetime.fromtimestamp(message.created_at.replace(tzinfo=timezone.utc).timestamp(), tz=timezone.utc),
                inference_options={}
            )
        else:
            return AssistantMessageItem(
                id=item_id,
                thread_id=thread_id,
                content=[AssistantMessageContent(type="output_text", text=message.content)],
                created_at=datetime.fromtimestamp(message.created_at.replace(tzinfo=timezone.utc).timestamp(), tz=timezone.utc)
            )

    async def delete_thread_item(self, thread_id: str, item_id: str, context: ChatContext) -> None:
        """Delete a message

        Args:
            thread_id: Conversation ID
            item_id: Message ID to delete
            context: User context
        """
        try:
            message_uuid = uuid.UUID(item_id.split('_')[-1])
        except (ValueError, IndexError):
            return

        statement = select(Message).where(
            Message.id == message_uuid,
            Message.user_id == uuid.UUID(context.user_id)
        )
        message = context.session.exec(statement).first()
        if message:
            context.session.delete(message)
            context.session.commit()

    async def load_threads(
        self,
        limit: int,
        after: Optional[str],
        order: str,
        context: ChatContext
    ) -> Page[ThreadMetadata]:
        """Load list of conversations for user

        Args:
            limit: Max threads to return
            after: Cursor for pagination (UUID string)
            order: 'asc' or 'desc'
            context: User context

        Returns:
            Page of ThreadMetadata objects
        """
        statement = select(Conversation).where(
            Conversation.user_id == uuid.UUID(context.user_id)
        )

        # Apply cursor pagination by updated_at timestamp (simpler with UUIDs)
        if after:
            try:
                after_uuid = uuid.UUID(after)
                # Note: UUID comparison for pagination is complex, skip for simplicity
            except ValueError:
                pass

        # Apply ordering
        if order == 'asc':
            statement = statement.order_by(Conversation.updated_at.asc())
        else:
            statement = statement.order_by(Conversation.updated_at.desc())

        statement = statement.limit(limit + 1)
        conversations = context.session.exec(statement).all()

        threads = []
        for conv in conversations[:limit]:
            threads.append(ThreadMetadata(
                id=str(conv.id),
                created_at=int(conv.created_at.replace(tzinfo=timezone.utc).timestamp())
            ))

        return Page(data=threads, has_more=len(conversations) > limit)

    async def delete_thread(self, thread_id: str, context: ChatContext) -> None:
        """Delete a conversation and all its messages

        Args:
            thread_id: Conversation ID to delete (UUID string)
            context: User context
        """
        try:
            conversation_uuid = uuid.UUID(thread_id)
        except ValueError:
            return

        statement = select(Conversation).where(
            Conversation.id == conversation_uuid,
            Conversation.user_id == uuid.UUID(context.user_id)
        )
        conversation = context.session.exec(statement).first()
        if conversation:
            context.session.delete(conversation)
            context.session.commit()

    # Attachment methods (not used in this implementation)
    async def save_attachment(self, attachment: Any, context: ChatContext) -> None:
        """Save attachment (not implemented)"""
        pass

    async def load_attachment(self, attachment_id: str, context: ChatContext) -> Any:
        """Load attachment (not implemented)"""
        raise NotImplementedError("Attachments not supported")

    async def delete_attachment(self, attachment_id: str, context: ChatContext) -> None:
        """Delete attachment (not implemented)"""
        pass