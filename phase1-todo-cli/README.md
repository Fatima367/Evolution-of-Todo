# Todo CLI Application

A menu-driven command-line todo application with SQLite persistence, built with Python 3.12+.

## Features

- ✅ Add, view, update, mark, and delete tasks
- 📊 Colorful table display with task priorities
- 💾 Persistent storage with SQLite
- 🎨 Rich terminal interface with inquirer menus
- ✓ Task status tracking (Pending, In-Progress, Completed)
- 🎯 Priority levels (Low, Medium, High)
- 📝 Detailed task descriptions
- 🔒 Input validation and error handling

## Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) or `pip`

## Installation

1. Clone the repository:
```bash
cd phase1-todo-cli
```

2. Install dependencies using `uv`:
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

### Running the Application

Using `uv`:
```bash
uv run python -m src.cli.main
```

Or if installed:
```bash
todo
```

### First Run

On first launch, the application will create a default task with your username to help you get started.

### Menu Options

1. **View Tasks** - Display all tasks in a formatted table
2. **Add Task** - Create a new task with title, description, and priority
3. **Update Task** - Modify an existing task's title or description
4. **Mark Task Status** - Change task status (Pending/In-Progress/Completed)
5. **Delete Task** - Remove a task permanently (with confirmation)
6. **Exit** - Close the application

### Task Fields

- **ID**: Auto-generated unique identifier
- **Title**: 1-200 characters (required)
- **Description**: Up to 500 characters (optional)
- **Status**: Pending, In-Progress, or Completed
- **Created Date**: Automatically set when task is created
- **Priority**: Low, Medium, or High

## Project Structure

```
phase1-todo-cli/
├── src/
│   ├── models/
│   │   └── task.py              # Task model with SQLModel
│   ├── services/
│   │   └── todo_service.py      # TodoApp service class
│   ├── cli/
│   │   └── main.py              # CLI interface
│   └── lib/
│       └── utils.py             # Utility functions
├── pyproject.toml               # Project configuration
├── README.md                    # This file
└── todo.db                      # SQLite database (created on first run)
```

## Database

The application uses SQLite for persistent storage. The database file (`todo.db`) is created automatically in the project root on first run.

## Development

### Running Tests

```bash
uv run python test_import.py
```

### Logging

The application logs operations to `todo_app.log` for debugging purposes.

### Error Handling

- Invalid inputs return exit code 2
- User-friendly error messages are displayed
- Graceful shutdown with Ctrl+C

## Technical Details

- **Language**: Python 3.12+
- **ORM**: SQLModel (SQLAlchemy 2.0)
- **UI**: Rich (terminal formatting)
- **Menus**: Inquirer (interactive prompts)
- **Database**: SQLite (file-based)

## License

Part of the Evolution of Todo project.
