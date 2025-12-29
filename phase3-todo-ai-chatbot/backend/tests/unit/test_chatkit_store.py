"""Unit tests for PostgreSQLStore (ChatKit store implementation)

These tests verify the PostgreSQL-backed conversation and message storage
that powers the ChatKit server.

Test Coverage:
- Thread (conversation) CRUD operations
- Message persistence and retrieval
- Thread history loading
- Pagination and ordering
- Data isolation
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone
from sqlmodel import Session

from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.auth.security import hash_password
from src.todo_chatkit.store import PostgreSQLStore, ChatContext
from chatkit.types import (
    ThreadMetadata,
    UserMessageItem,
    AssistantMessageItem,
    UserMessageTextContent
)


@pytest.fixture
def test_user(session: Session):
    """Create a test user for store testing"""
    user = User(
        id=uuid4(),
        email="storetest@example.com",
        name="Store Test User",
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
async def test_generate_thread_id(store: PostgreSQLStore, chat_context: ChatContext):
    """Test thread ID generation"""
    thread_id = store.generate_thread_id(chat_context)

    # Should be a valid UUID string
    assert isinstance(thread_id, str)
    assert len(thread_id) > 0
    uuid4_obj = uuid4()  # Will raise if invalid format


@pytest.mark.asyncio
async def test_generate_item_id(store: PostgreSQLStore, chat_context: ChatContext):
    """Test item ID generation"""
    thread = ThreadMetadata(id="1", created_at=datetime.now(timezone.utc))
    item_id = store.generate_item_id("message", thread, chat_context)

    assert isinstance(item_id, str)
    assert item_id.startswith("message_")


@pytest.mark.asyncio
async def test_save_and_load_thread(store: PostgreSQLStore, chat_context: ChatContext, session: Session):
    """Test creating and loading a conversation"""
    # Create thread metadata
    thread = ThreadMetadata(
        id=store.generate_thread_id(chat_context),
        created_at=datetime.now(timezone.utc)
    )

    # Save thread
    await store.save_thread(thread, chat_context)

    # Thread ID should be updated with actual DB ID
    assert thread.id is not None

    # Load thread
    loaded_thread = await store.load_thread(thread.id, chat_context)

    assert loaded_thread.id == thread.id
    assert loaded_thread.created_at is not None


@pytest.mark.asyncio
async def test_save_thread_updates_existing(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test updating an existing conversation"""
    # Create conversation directly in DB
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    original_updated_at = conversation.updated_at

    # Wait a moment to ensure timestamp difference
    import time
    time.sleep(0.1)

    # Update via store
    thread = ThreadMetadata(
        id=str(conversation.id),
        created_at=conversation.created_at.replace(tzinfo=timezone.utc)
    )
    await store.save_thread(thread, chat_context)

    # Verify updated_at changed
    session.refresh(conversation)
    assert conversation.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_load_nonexistent_thread(store: PostgreSQLStore, chat_context: ChatContext):
    """Test loading a thread that doesn't exist returns empty metadata"""
    loaded_thread = await store.load_thread("99999", chat_context)

    # Should return metadata but thread won't exist in DB
    assert loaded_thread.id == "99999"
    assert loaded_thread.created_at is not None


@pytest.mark.asyncio
async def test_load_thread_enforces_user_isolation(store: PostgreSQLStore, session: Session, test_user: User):
    """Test that users can only load their own conversations"""
    # Create conversation for test_user
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()

    # Create different user
    other_user = User(
        id=uuid4(),
        email="other@example.com",
        name="Other User",
        password_hash=hash_password("pass"),
        is_active=True
    )
    session.add(other_user)
    session.commit()

    # Try to load with different user context
    other_context = ChatContext(user_id=str(other_user.id), session=session)
    loaded = await store.load_thread(str(conversation.id), other_context)

    # Should return empty metadata (unauthorized)
    assert loaded.id == str(conversation.id)


@pytest.mark.asyncio
async def test_add_and_load_thread_items(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test adding and loading messages"""
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

    # Create user message
    user_msg = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Hello AI")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )

    # Add message
    await store.add_thread_item(thread_id, user_msg, chat_context)

    # Load messages
    page = await store.load_thread_items(thread_id, None, 10, "asc", chat_context)

    assert len(page.data) == 1
    assert page.data[0].content[0].text == "Hello AI"


@pytest.mark.asyncio
async def test_add_thread_item_user_and_assistant(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test adding both user and assistant messages"""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add user message
    user_msg = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="User message")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, user_msg, chat_context)

    # Add assistant message
    assistant_msg = AssistantMessageItem(
        id="msg_2",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Assistant message")],
        created_at=datetime.now(timezone.utc)
    )
    await store.add_thread_item(thread_id, assistant_msg, chat_context)

    # Load and verify
    page = await store.load_thread_items(thread_id, None, 10, "asc", chat_context)

    assert len(page.data) == 2
    assert isinstance(page.data[0], UserMessageItem)
    assert isinstance(page.data[1], AssistantMessageItem)


@pytest.mark.asyncio
async def test_load_thread_items_pagination(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test message pagination"""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add 5 messages
    for i in range(5):
        msg = UserMessageItem(
            id=f"msg_{i}",
            thread_id=thread_id,
            content=[UserMessageTextContent(type="input_text", text=f"Message {i}")],
            created_at=datetime.now(timezone.utc),
            inference_options={}
        )
        await store.add_thread_item(thread_id, msg, chat_context)

    # Load with limit=2
    page = await store.load_thread_items(thread_id, None, 2, "asc", chat_context)

    assert len(page.data) == 2
    assert page.has_more is True


@pytest.mark.asyncio
async def test_load_thread_items_ordering(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test message ordering (asc vs desc)"""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add messages
    for i in range(3):
        msg = UserMessageItem(
            id=f"msg_{i}",
            thread_id=thread_id,
            content=[UserMessageTextContent(type="input_text", text=f"Message {i}")],
            created_at=datetime.now(timezone.utc),
            inference_options={}
        )
        await store.add_thread_item(thread_id, msg, chat_context)
        import time
        time.sleep(0.01)  # Ensure different timestamps

    # Load ascending
    page_asc = await store.load_thread_items(thread_id, None, 10, "asc", chat_context)

    # Load descending
    page_desc = await store.load_thread_items(thread_id, None, 10, "desc", chat_context)

    assert len(page_asc.data) == 3
    assert len(page_desc.data) == 3

    # Order should be reversed
    assert page_asc.data[0].content[0].text == "Message 0"
    assert page_desc.data[0].content[0].text == "Message 2"


@pytest.mark.asyncio
async def test_load_thread_items_with_cursor(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test cursor-based pagination"""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    thread_id = str(conversation.id)

    # Add messages and track IDs
    message_ids = []
    for i in range(4):
        msg = UserMessageItem(
            id=f"msg_{i}",
            thread_id=thread_id,
            content=[UserMessageTextContent(type="input_text", text=f"Message {i}")],
            created_at=datetime.now(timezone.utc),
            inference_options={}
        )
        await store.add_thread_item(thread_id, msg, chat_context)

    # Load first page
    page1 = await store.load_thread_items(thread_id, None, 2, "asc", chat_context)
    assert len(page1.data) == 2

    # Get cursor from last item
    cursor = page1.data[-1].id

    # Load next page
    page2 = await store.load_thread_items(thread_id, cursor, 2, "asc", chat_context)
    assert len(page2.data) == 2


@pytest.mark.asyncio
async def test_save_and_load_item(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test updating an existing message"""
    # Create conversation and message
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()

    message = Message(
        user_id=test_user.id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Original content",
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    thread_id = str(conversation.id)
    item_id = f"msg_{message.id}"

    # Load item
    loaded = await store.load_item(thread_id, item_id, chat_context)
    assert loaded.content[0].text == "Original content"

    # Update item
    loaded.content = [UserMessageTextContent(type="input_text", text="Updated content")]
    await store.save_item(thread_id, loaded, chat_context)

    # Verify update
    session.refresh(message)
    assert message.content == "Updated content"


@pytest.mark.asyncio
async def test_load_item_not_found(store: PostgreSQLStore, chat_context: ChatContext):
    """Test loading non-existent message raises error"""
    with pytest.raises(ValueError, match="Message not found"):
        await store.load_item("1", "msg_99999", chat_context)


@pytest.mark.asyncio
async def test_load_item_invalid_id(store: PostgreSQLStore, chat_context: ChatContext):
    """Test loading with invalid item ID raises error"""
    with pytest.raises(ValueError, match="Invalid item ID"):
        await store.load_item("1", "invalid", chat_context)


@pytest.mark.asyncio
async def test_delete_thread_item(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test deleting a message"""
    # Create conversation and message
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()

    message = Message(
        user_id=test_user.id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="To be deleted",
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    thread_id = str(conversation.id)
    item_id = f"msg_{message.id}"

    # Delete
    await store.delete_thread_item(thread_id, item_id, chat_context)

    # Verify deletion
    session.expire_all()
    deleted = session.get(Message, message.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_load_threads(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test loading list of conversations"""
    # Create multiple conversations
    for i in range(3):
        conv = Conversation(
            user_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conv)
    session.commit()

    # Load threads
    page = await store.load_threads(10, None, "desc", chat_context)

    assert len(page.data) >= 3
    assert all(isinstance(t, ThreadMetadata) for t in page.data)


@pytest.mark.asyncio
async def test_load_threads_pagination(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test conversation list pagination"""
    # Create 5 conversations
    for i in range(5):
        conv = Conversation(
            user_id=test_user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conv)
    session.commit()

    # Load with limit
    page = await store.load_threads(2, None, "desc", chat_context)

    assert len(page.data) == 2
    assert page.has_more is True


@pytest.mark.asyncio
async def test_load_threads_user_isolation(store: PostgreSQLStore, session: Session, test_user: User):
    """Test that users only see their own conversations"""
    # Create conversation for test_user
    conv1 = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv1)

    # Create other user and their conversation
    other_user = User(
        id=uuid4(),
        email="other@example.com",
        name="Other User",
        password_hash=hash_password("pass"),
        is_active=True
    )
    session.add(other_user)
    session.commit()

    conv2 = Conversation(
        user_id=other_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conv2)
    session.commit()

    # Load as test_user
    context1 = ChatContext(user_id=str(test_user.id), session=session)
    page1 = await store.load_threads(10, None, "desc", context1)

    # Load as other_user
    context2 = ChatContext(user_id=str(other_user.id), session=session)
    page2 = await store.load_threads(10, None, "desc", context2)

    # Each should only see their own
    user1_ids = [t.id for t in page1.data]
    user2_ids = [t.id for t in page2.data]

    assert str(conv1.id) in user1_ids
    assert str(conv1.id) not in user2_ids
    assert str(conv2.id) in user2_ids
    assert str(conv2.id) not in user1_ids


@pytest.mark.asyncio
async def test_delete_thread(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test deleting a conversation"""
    # Create conversation with messages
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    message = Message(
        user_id=test_user.id,
        conversation_id=conversation.id,
        role=MessageRole.USER,
        content="Test",
        created_at=datetime.utcnow()
    )
    session.add(message)
    session.commit()

    thread_id = str(conversation.id)

    # Delete thread
    await store.delete_thread(thread_id, chat_context)

    # Verify deletion (cascade should delete messages too)
    session.expire_all()
    assert session.get(Conversation, conversation.id) is None
    assert session.get(Message, message.id) is None


@pytest.mark.asyncio
async def test_delete_thread_user_isolation(store: PostgreSQLStore, session: Session, test_user: User):
    """Test that users cannot delete other users' conversations"""
    # Create conversation for test_user
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()

    # Create other user
    other_user = User(
        id=uuid4(),
        email="other@example.com",
        name="Other User",
        password_hash=hash_password("pass"),
        is_active=True
    )
    session.add(other_user)
    session.commit()

    # Try to delete as other user
    other_context = ChatContext(user_id=str(other_user.id), session=session)
    await store.delete_thread(str(conversation.id), other_context)

    # Conversation should still exist
    session.expire_all()
    assert session.get(Conversation, conversation.id) is not None


@pytest.mark.asyncio
async def test_add_thread_item_updates_conversation_timestamp(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test that adding a message updates conversation updated_at"""
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

    # Add message
    thread_id = str(conversation.id)
    msg = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[UserMessageTextContent(type="input_text", text="Hello")],
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg, chat_context)

    # Verify timestamp updated
    session.refresh(conversation)
    assert conversation.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_add_thread_item_ignores_empty_content(store: PostgreSQLStore, chat_context: ChatContext, session: Session, test_user: User):
    """Test that empty messages are not persisted"""
    conversation = Conversation(
        user_id=test_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    session.add(conversation)
    session.commit()

    thread_id = str(conversation.id)

    # Try to add empty message
    msg = UserMessageItem(
        id="msg_1",
        thread_id=thread_id,
        content=[],  # Empty content
        created_at=datetime.now(timezone.utc),
        inference_options={}
    )
    await store.add_thread_item(thread_id, msg, chat_context)

    # Verify no message was created
    page = await store.load_thread_items(thread_id, None, 10, "asc", chat_context)
    assert len(page.data) == 0
