
import uuid
from sqlmodel import Session, create_engine, SQLModel
from src.todo_chatkit.tools import create_task_tools, TaskToolContext
from src.models.task import Task
from src.models.user import User

# Setup in-memory DB
engine = create_engine("sqlite:///:memory:")
SQLModel.metadata.create_all(engine)

def verify_tools():
    with Session(engine) as session:
        # Create user
        user_id = str(uuid.uuid4())

        # Create tools
        tools = create_task_tools(session, user_id)
        add_task = next(tool for tool in tools if tool.name == "add_task")

        print(f"Verifying tool: {add_task.name}")

        # Mock Context
        class MockCtx:
            def __init__(self, session, user_id):
                self.session = session
                self.user_id = user_id

        ctx = MockCtx(session, user_id)

        # Execute tool
        # We need to pass ctx because our tool expects it
        try:
            result = add_task.func(ctx, title="Verify Task", priority="high")
            print(f"Result: {result}")

            # Verify DB
            task = session.query(Task).first()
            if task and task.title == "Verify Task":
                print("SUCCESS: Task found in database")
            else:
                print("FAILURE: Task NOT found in database")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    verify_tools()
