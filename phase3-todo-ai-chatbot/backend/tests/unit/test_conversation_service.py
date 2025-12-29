"""Tests for User Story 2 - Conversation Context Persistence

These tests verify that conversation history persists across sessions
and survives server restarts.

Test Coverage:
- T060: Conversation persists across multiple message exchanges
- T061: Conversation updated_at timestamp updates on each message
- T062: Conversation can be resumed after server restart (simulated)
- T063: Messages are ordered by created_at ascending
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlmodel import Session, select

from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.auth.security import hash_password
from src.todo_chatkit.store import PostgreSQLStore, ChatContext
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    UserMessageTextContent,
    AssistantMessageContent
)


@pytest.fixture
def test_user(session: Session):
    """Create a test user for conversation testing"""
    user = User(
        id=uuid4(),
        email="converation_test@example.com",
        name="Conversation Test User",
        password_hash=hash_password("testpassword123"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def chat_context(session: Session, test_user: User):
    """Create chat context for store operations"""
    return ChatContext(
        user_id=str(test_user.id),
        session=session
    )


@pytest.fixture
def store():
    """Create PostgreSQLStore instance"""
    return PostgreSQLStore()


@pytest.mark.asyncio
async def test_conversation_persists_across_messages(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """T060: Test conversation persists across multiple message exchanges"""
    # Create conversation
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add first message
    user_msg1 = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="First message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, user_msg1, chat_context)

    # Add second message
    user_msg2 = UserMessageItem(
        id="msg_2",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Second message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, user_msg2, chat_context)

    # Add assistant response
    assistant_msg = AssistantMessageItem(
        id="msg_3",
        thread_id=thread_id,
        content=[AssistantMessageContent(type="output_text", text="Response to second message")],
        created_at=datetime.now(timezone.utc)
    )
    await store.add_thread_item(thread_id, assistant_msg, chat_context)

    # Load and verify all messages persist
    page = await store.load_thread_items(thread_id, None, 100, "asc", chat_context)

    assert len(page.data) == 3
    assert page.data[0].content[0].text == "First message"
    assert page.data[1].content[0].text == "Second message"
    assert page.data[2].content[0].text == "Response to second message"


@pytest.mark.asyncio
async def test_conversation_updated_at_updates_on_each_message(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """T061: Test conversation updated_at timestamp updates on each message"""
    # Create conversation
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    original_updated_at = conversation.updated_at

    import time
    time.sleep(0.1)

    thread_id = str(conversation.id)

    # Add first message
    msg1 = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Message 1")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg1, chat_context)

    # Verify updated_at changed
    session.refresh(conversation)
    assert conversation.updated_at > original_updated_at

    first_update = conversation.updated_at

    time.sleep(0.1)

    # Add second message
    msg2 = UserMessageItem(
        id="msg_2",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Message 2")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg2, chat_context)

    # Verify updated_at changed again
    session.refresh(conversation)
    assert conversation.updated_at > first_update


@pytest.mark.asyncio
async def test_conversation_resume_after_restart(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """T062: Test conversation can be resumed after server restart (simulated)"""
    # Create conversation and messages
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add messages before "restart"
    msg1 = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Pre-restart message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg1, chat_context)

    # Simulate server restart by expiring session cache
    session.expire_all()

    # Load conversation (as if resuming after restart)
    loaded_thread = await store.load_thread(thread_id, chat_context)
    assert loaded_thread.id == thread_id

    # Load messages
    page = await store.load_thread_items(thread_id, None, 100, "asc", chat_context)
    assert len(page.data) == 1
    assert page.data[0].content[0].text == "Pre-restart message"

    # Add new message after "restart"
    msg2 = UserMessageItem(
        id="msg_2",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Post-restart message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg2, chat_context)

    # Verify both messages exist
    page = await store.load_thread_items(thread_id, None, 100, "asc", chat_context)
    assert len(page.data) == 2


@pytest.mark.asyncio
async def test_messages_ordered_by_created_at_ascending(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """T063: Test messages are ordered by created_at ascending"""
    # Create conversation
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add messages in specific order
    timestamps = []
    for i in range(5):
        msg = UserMessageItem(
            id=f"msg_{i}",
            thread_id=thread_id,
            content=[UserMessageTextContent(type="input_text", text=f"Message {i}")],
            created_at=datetime.now(timezone.utc),
            inference_options={}
        )
        await store.add_thread_item(thread_id, msg, chat_context)
        timestamps.append(msg.created_at)
        import time
        time.sleep(0.01)  # Ensure different timestamps

    # Load in ascending order
    page = await store.load_thread_items(thread_id, None, 100, "asc", chat_context)

    assert len(page.data) == 5
    # Verify ascending order
    for i in range(5):
        assert page.data[i].content[0].text == f"Message {i}"


@pytest.mark.asyncio
async def test_conversation_context_includes_thread_id(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test that conversation context properly includes thread_id for tool operations"""
    # Create conversation
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Load thread
    loaded = await store.load_thread(thread_id, chat_context)

    # Thread ID should be preserved
    assert loaded.id == thread_id
    assert loaded.created_at is not None


@pytest.mark.asyncio
async def test_multiple_conversations_independent(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test that multiple conversations for same user are independent"""
    # Create two conversations
    conv1 = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    conv2 = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv1)
    session.add(conv2)
    session.commit()
    session.refresh(conv1)
    session.refresh(conv2)

    thread_id_1 = str(conv1.id)
    thread_id_2 = str(conv2.id)

    # Add different messages to each conversation
    msg1 = UserMessageItem(
        id="msg_1",
        thread_id=thread_id_1,
        content=[UserMessageTextContent(type="input_text", text="Conversation 1 message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id_1, msg1, chat_context)

    msg2 = UserMessageItem(
        id="msg_2",
        thread_id=thread_id_2,
        content=[UserMessageTextContent(type="input_text", text="Conversation 2 message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id_2, msg2, chat_context)

    # Load each conversation separately
    page1 = await store.load_thread_items(thread_id_1, None, 100, "asc", chat_context)
    page2 = await store.load_thread_items(thread_id_2, None, 100, "asc", chat_context)

    assert len(page1.data) == 1
    assert page1.data[0].content[0].text == "Conversation 1 message"

    assert len(page2.data) == 1
    assert page2.data[0].content[0].text == "Conversation 2 message"
