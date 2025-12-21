"""Simple test to verify imports work."""

try:
    print("Testing imports...")

    # Test model imports
    from src.models import Task, PriorityEnum, StatusEnum, get_engine, create_db_and_tables
    print("✓ Models import successfully")

    # Test service imports
    from src.services import TodoApp
    print("✓ Services import successfully")

    # Test lib imports
    from src.lib.utils import validate_title, validate_description, validate_priority, validate_status
    print("✓ Utils import successfully")

    # Test CLI imports
    from src.cli.main import main
    print("✓ CLI imports successfully")

    print("\n✅ All imports successful!")

    # Test basic functionality
    print("\nTesting basic functionality...")
    app = TodoApp()
    print("✓ TodoApp initialized")

    tasks = app.view_tasks()
    print(f"✓ Found {len(tasks)} tasks (including default task)")

    if tasks:
        print(f"  - Default task: '{tasks[0].title}'")

    print("\n✅ Basic functionality test passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
