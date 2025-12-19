# Quickstart Guide: Todo CLI Application

## Prerequisites
- Python 3.13+ installed
- `uv` package manager installed

## Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install sqlmodel rich inquirer-python
   ```

## Running the Application
```bash
cd /path/to/project
python src/cli/main.py
```

## Initial Usage
1. The application starts with a colorful menu interface
2. Use number keys or arrow keys to navigate options
3. Follow prompts to add, view, update, mark, or delete tasks

## Development
- Main application logic: `src/services/todo_service.py`
- Data models: `src/models/task.py`
- CLI interface: `src/cli/main.py`
- Utility functions: `src/lib/utils.py`

## Testing
```bash
pytest tests/
```

## Default Task
On first run, the application creates a personalized default task: "[User's Name]'s first todo" (FR-016)