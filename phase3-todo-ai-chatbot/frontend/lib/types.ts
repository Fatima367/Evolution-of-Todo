export type TaskStatus = "pending" | "in_progress" | "completed";
export type TaskPriority = "low" | "medium" | "high" | "urgent";

// Sort field options for tasks
export type SortField = "created_at" | "due_date" | "priority" | "title";

// Sort direction options
export type SortDirection = "asc" | "desc";

// Sort option configuration
export interface SortOption {
  field: SortField;
  direction: SortDirection;
}

// Sort configuration for UI dropdown
export interface SortConfig {
  label: string;
  value: SortField;
  icon?: string;
  defaultDirection: SortDirection;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  tags: string[] | null;
  user_id: string;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  tags?: string[];
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface TasksResponse {
  tasks: Task[];
  total: number;
}
