import { Task, TaskCreate, TaskUpdate, TasksResponse, User, UserCreate, UserLogin, TokenResponse, SortField, SortDirection } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      try {
        const errorData = await response.json();
        // Handle different possible error response formats
        if (typeof errorData === 'string') {
          errorMessage = errorData;
        } else if (errorData?.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMessage = errorData.detail.map((err: { loc: (string | number)[], msg: string }) => {
              const field = err.loc && err.loc.length > 1 ? String(err.loc[1]).replace(/_/g, ' ') : 'field';
              return `${field.charAt(0).toUpperCase() + field.slice(1)}: ${err.msg}`;
            }).join('; ');
          } else {
            errorMessage = String(errorData.detail);
          }
        } else if (errorData?.message) {
          errorMessage = String(errorData.message);
        } else if (errorData?.error) {
          errorMessage = String(errorData.error);
        } else if (typeof errorData === 'object') {
          // Extract the most relevant field from the error object
          const possibleFields = ['detail', 'message', 'error', 'msg', 'reason'];
          for (const field of possibleFields) {
            if (errorData[field]) {
              errorMessage = String(errorData[field]);
              break;
            }
          }
          // If no known field found, try to create a readable string
          if (errorMessage === `HTTP ${response.status}`) {
            errorMessage = Object.entries(errorData)
              .filter(([_, value]) => value != null && typeof value !== 'object' && typeof value !== 'function')
              .map(([key, value]) => `${key}: ${value}`)
              .join(', ');

            if (!errorMessage) {
              errorMessage = JSON.stringify(errorData, null, 2);
            }
          }
        }
      } catch (jsonError) {
        // If parsing JSON fails, use status text or default message
        errorMessage = response.statusText || 'Request failed';
      }
      throw new Error(errorMessage);
    }

    if (response.status === 204) {
      return null as T;
    }

    return response.json();
  }

  // Auth endpoints
  async register(data: UserCreate): Promise<TokenResponse> {
    return this.request<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(credentials: UserLogin): Promise<TokenResponse> {
    return this.request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async logout(): Promise<void> {
    return this.request<void>('/auth/logout', { method: 'POST' });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  async updateCurrentUser(data: {
    name?: string;
    email_notifications?: boolean;
    task_reminders?: boolean;
    weekly_summary?: boolean;
  }): Promise<User> {
    return this.request<User>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    return this.request<void>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      }),
    });
  }

  async deleteAccount(password: string): Promise<void> {
    return this.request<void>('/auth/me', {
      method: 'DELETE',
      body: JSON.stringify({
        password: password
      }),
    });
  }

  // Task endpoints
  async getTasks(params?: {
    status?: string;
    priority?: string;
    is_favorite?: boolean;
    sort_by?: SortField;
    sort_order?: SortDirection;
    limit?: number;
    offset?: number;
  }): Promise<TasksResponse> {
    const query = new URLSearchParams();
    if (params?.status) query.append('status', params.status);
    if (params?.priority) query.append('priority', params.priority);
    if (params?.is_favorite !== undefined) query.append('is_favorite', params.is_favorite.toString());
    if (params?.sort_by) query.append('sort_by', params.sort_by);
    if (params?.sort_order) query.append('sort_order', params.sort_order);
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.offset) query.append('offset', params.offset.toString());

    return this.request<TasksResponse>(`/tasks/?${query}`);
  }

  async getTask(id: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`);
  }

  async createTask(data: TaskCreate): Promise<Task> {
    return this.request<Task>('/tasks/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: TaskUpdate): Promise<Task> {
    return this.request<Task>(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async toggleFavorite(id: string): Promise<Task> {
    return this.request<Task>(`/tasks/${id}/favorite`, {
      method: 'PATCH',
    });
  }

  async deleteTask(id: string): Promise<void> {
    return this.request<void>(`/tasks/${id}`, { method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
