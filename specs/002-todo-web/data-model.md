# Data Model: Todo Full-Stack Web Application

## Entity: User

### Fields
- `id` (UUID, Primary Key) - Unique identifier for the user
- `email` (String, Unique, Not Null) - User's email address for authentication
- `name` (String, Not Null) - User's display name
- `password_hash` (String, Not Null) - Hashed password using secure algorithm
- `created_at` (DateTime, Not Null) - Timestamp when user account was created
- `updated_at` (DateTime, Not Null) - Timestamp when user account was last updated
- `is_active` (Boolean, Not Null, Default: True) - Whether the user account is active

### Relationships
- One-to-Many: User has many Tasks (user.tasks)

### Validation Rules
- Email must be a valid email format
- Email must be unique across all users
- Name must be 1-100 characters
- Password must meet security requirements (min 8 characters, complexity)

## Entity: Task

### Fields
- `id` (UUID, Primary Key) - Unique identifier for the task
- `title` (String, Not Null) - Task title/description
- `description` (Text, Nullable) - Detailed description of the task
- `status` (String, Not Null, Default: "pending") - Task status: "pending", "in_progress", "completed"
- `priority` (String, Not Null, Default: "medium") - Task priority: "low", "medium", "high", "urgent"
- `due_date` (DateTime, Nullable) - Optional deadline for the task
- `tags` (JSON, Nullable) - Array of tags for the task (e.g., ["work", "personal"])
- `user_id` (UUID, Foreign Key, Not Null) - Reference to the owning user
- `created_at` (DateTime, Not Null) - Timestamp when task was created
- `updated_at` (DateTime, Not Null) - Timestamp when task was last updated
- `completed_at` (DateTime, Nullable) - Timestamp when task was marked as completed

### Relationships
- Many-to-One: Task belongs to a User (task.user)

### Validation Rules
- Title must be 1-200 characters
- Description must be 0-10000 characters if provided
- Status must be one of: "pending", "in_progress", "completed"
- Priority must be one of: "low", "medium", "high", "urgent"
- Due date must be in the future if provided
- Tags must be an array of strings, max 10 tags, each tag max 50 characters
- User_id must reference an existing active user

### State Transitions
- Status can transition from: "pending" → "in_progress" → "completed"
- Status can transition from: "in_progress" → "pending"
- When status changes to "completed", completed_at is set to current timestamp
- When status changes from "completed" to any other status, completed_at is set to null

## Database Constraints

### Primary Keys
- All entities use UUID primary keys for consistency and security

### Foreign Keys
- Task.user_id references User.id with CASCADE delete (when user is deleted, their tasks are also deleted)

### Indexes
- User.email: Unique index for fast authentication lookups
- Task.user_id: Index for efficient user-specific queries (required for data isolation)
- Task.created_at: Index for chronological sorting
- Task.status: Index for filtering by status
- Task.due_date: Index for due date queries
- Task.priority: Index for priority-based sorting

### Data Isolation
- All task queries must include WHERE clause filtering by user_id to enforce data isolation
- Application logic must validate that users can only access/modify tasks they own
- API endpoints must validate that the authenticated user matches the task's user_id before operations

## API Schema Mappings

### User Schemas
- **UserCreate**: email, name, password (excludes password_hash for security)
- **UserRead**: id, email, name, created_at, updated_at (excludes password fields)
- **UserUpdate**: name only (email changes require separate verification process)

### Task Schemas
- **TaskCreate**: title, description, priority, due_date, tags (status defaults to "pending")
- **TaskRead**: all fields including user information
- **TaskUpdate**: any subset of title, description, status, priority, due_date, tags