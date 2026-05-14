
import uuid
from sqlmodel import Session, create_engine, SQLModel
from src.todo_chatkit.tools import create_task_tools
from src.models.task import Task
from src.models.user import User

# Test data constants
TEST_TASK_TITLE = "Read book"

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

class MockCtx:
    def __init__(self, session, user_id):
        self.session = session
        self.user_id = user_id

def verify_named_references():
    with Session(engine) as session:
        # Create user
        user_uuid = uuid.uuid4()
        user_id = str(user_uuid)
        user = User(id=user_uuid, email="test@example.com", name="Test User", password_hash="hash")
        session.add(user)
        session.commit()

        # Create tools
        tools = create_task_tools(session, user_id)
        add_task = next(tool for tool in tools if tool.name == "add_task")
        complete_task = next(tool for tool in tools if tool.name == "complete_task")
        update_task = next(tool for tool in tools if tool.name == "update_task")
        delete_task = next(tool for tool in tools if tool.name == "delete_task")

        ctx = MockCtx(session, user_id)

        print("--- 1. Testing Unique Title Match ---")
        task1 = add_task.func(ctx, title="Buy groceries", description="Milk and eggs")
        print(f"Created task: {task1['task_id']}")

        # Complete by title
        res = complete_task.func(ctx, task_id="Buy groceries")
        print(f"Complete result: {res['status']}")

        # Verify
        completed_task = session.get(Task, task1['task_id'])
        print(f"Task status in DB: {completed_task.status}")

        print("\n--- 2. Testing Fuzzy Match ---")
        task2 = add_task.func(ctx, title="Finish the project report", priority="high")

        # Update by partial title
        res = update_task.func(ctx, task_id="project report", priority="urgent")
        print(f"Update result: {res['status']}, Priority: {res.get('priority')}")

        # Verify
        updated_task = session.get(Task, task2['task_id'])
        print(f"Task priority in DB: {updated_task.priority}")

        print("\n--- 3. Testing Ambiguous Matches ---")
        add_task.func(ctx, title=TEST_TASK_TITLE)
        add_task.func(ctx, title=TEST_TASK_TITLE)

        res = complete_task.func(ctx, task_id=TEST_TASK_TITLE)
        print(f"Ambiguous result status: {res['status']}")
        print(f"Matches found: {len(res.get('matches', []))}")

        print("\n--- 4. Testing Whitespace Handling ---")
        task3 = add_task.func(ctx, title="Clean the house")
        res = delete_task.func(ctx, task_id="  Clean the house  ")
        print(f"Delete result: {res['status']}")

        deleted_task = session.get(Task, task3['task_id'])
        print(f"Is task deleted? {deleted_task is None}")

if __name__ == "__main__":
    verify_named_references()
