# CLI Interface Contracts: Todo CLI Application

## Overview
This document defines the interface contracts for the Todo CLI application, specifying the expected behavior of all user interactions and system responses.

## Command Line Interface (CLI) Contracts

### 1. Main Menu Interface
**Contract**: `display_menu() -> str`

**Input**: None
**Output**: Menu selection string (1-5) or exit command
**Behavior**:
- Displays colorful menu with options:
  1. View Tasks
  2. Add Task
  3. Update Task
  4. Mark Task Status
  5. Delete Task
  6. Exit
- Uses rich formatting for visual appeal (FR-012)
- Returns user selection as string

### 2. Task Management Contracts

#### 2.1 Add Task
**Contract**: `add_task(title: str, description: str, priority: str) -> Task`

**Input Parameters**:
- `title`: String, 1-200 characters (FR-009)
- `description`: String, optional, max 500 characters (FR-010)
- `priority`: String, one of "Low", "Medium", "High" (case-insensitive)

**Output**: Task object with assigned ID and creation timestamp
**Success Response**: Success message with new task details
**Error Handling**:
- Invalid title length → Error message + exit code 2 (FR-011)
- Invalid priority → Error message + exit code 2 (FR-011)

#### 2.2 View Tasks
**Contract**: `view_tasks() -> List[Task]`

**Input**: None
**Output**: Formatted table display of all tasks
**Success Response**: Table with columns: ID | Title | Description | Status ✓/✗ | Created Date | Priority (FR-004)
- If no tasks exist → Display "No tasks" message (FR-093)
- Color-coded status indicators
- Formatted with rich library for visual appeal

#### 2.3 Update Task
**Contract**: `update_task(task_id: int, title: str, description: str) -> Task`

**Input Parameters**:
- `task_id`: Integer, valid existing task ID
- `title`: String, 1-200 characters (FR-009)
- `description`: String, optional, max 500 characters (FR-010)

**Output**: Updated Task object
**Success Response**: Success confirmation message
**Error Handling**:
- Invalid task_id → "Invalid ID" error + exit code 2 (FR-090)
- Non-existent task → 404 error with helpful message (FR-091)
- Invalid input → Appropriate error message + exit code 2 (FR-011)

#### 2.4 Mark Task Status
**Contract**: `mark_task(task_id: int, status: str) -> Task`

**Input Parameters**:
- `task_id`: Integer, valid existing task ID
- `status`: String, one of "Pending", "In-Progress", "Completed" (case-insensitive)

**Output**: Task object with updated status
**Success Response**: Success confirmation message
**Error Handling**:
- Invalid task_id → "Invalid ID" error + exit code 2 (FR-090)
- Invalid status → Error message + exit code 2
- Non-existent task → 404 error with helpful message (FR-091)

#### 2.5 Delete Task
**Contract**: `delete_task(task_id: int) -> bool`

**Input Parameters**:
- `task_id`: Integer, valid existing task ID

**Output**: Boolean indicating successful deletion
**Success Response**: Confirmation message that task was deleted
**Error Handling**:
- Invalid task_id → "Invalid ID" error + exit code 2 (FR-090)
- Non-existent task → 404 error with helpful message (FR-091)

### 3. Input Validation Contracts

#### 3.1 Title Validation
**Contract**: `validate_title(title: str) -> bool`

**Input**: String title
**Output**: Boolean indicating validity
**Validation Rules**:
- Length: 1-200 characters (FR-009)
- Return True if valid, False if invalid

#### 3.2 Description Validation
**Contract**: `validate_description(description: str) -> bool`

**Input**: String description
**Output**: Boolean indicating validity
**Validation Rules**:
- Length: max 500 characters (FR-010)
- Return True if valid, False if invalid

#### 3.3 Priority Validation
**Contract**: `validate_priority(priority: str) -> bool`

**Input**: String priority
**Output**: Boolean indicating validity
**Validation Rules**:
- Must be one of: "Low", "Medium", "High" (case-insensitive)
- Return True if valid, False if invalid

#### 3.4 Status Validation
**Contract**: `validate_status(status: str) -> bool`

**Input**: String status
**Output**: Boolean indicating validity
**Validation Rules**:
- Must be one of: "Pending", "In-Progress", "Completed" (case-insensitive)
- Return True if valid, False if invalid

### 4. Error Handling Contracts

#### 4.1 General Error Handling
**Contract**: `handle_error(error_type: str, message: str) -> None`

**Input Parameters**:
- `error_type`: String indicating type of error
- `message`: Error message to display
**Output**: None
**Behavior**:
- Displays user-friendly error message
- Returns appropriate exit code (2 for validation errors) (FR-011)
- Does not crash application (FR-017)

### 5. Persistence Contracts (SQLModel)

#### 5.1 Database Connection
**Contract**: `get_db_engine() -> Engine`

**Input**: None
**Output**: SQLModel database engine
**Behavior**:
- Phase I: In-memory SQLite (`sqlite:///:memory:`)
- Phase II+: File-based SQLite (`sqlite:///todo.db`)
- Returns properly configured engine for Task operations

#### 5.2 Task CRUD Operations
**Contract**: `create_task(task: Task) -> Task`

**Input**: Task object with title, description, priority
**Output**: Task object with assigned ID and creation timestamp

**Contract**: `read_tasks() -> List[Task]`

**Input**: None
**Output**: List of all stored Task objects

**Contract**: `update_task_db(task_id: int, task_data: dict) -> Task`

**Input**: Task ID and update data
**Output**: Updated Task object

**Contract**: `delete_task_db(task_id: int) -> bool`

**Input**: Task ID
**Output**: Boolean indicating successful deletion

## Exit Codes
- `0`: Success
- `2`: Validation error or invalid input (FR-011)

## Default Behavior
- On first run, creates personalized default task "[User's Name]'s first todo" (FR-016)
- Application maintains in-memory state during session (Phase I)
- Colorful UI elements throughout application (FR-012)
- Modular architecture with Task dataclass and TodoApp class (FR-013)