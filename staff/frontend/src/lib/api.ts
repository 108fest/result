const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export type User = {
  id: number;
  full_name: string;
  email: string | null;
  username: string | null;
  kpi_score: number;
  photo_url: string;
  role: "admin" | "junior_dev" | "senior_dev";
  level: number;
  promotion_requested: boolean;
  promotion_requested_at: string | null;
  break_until: string | null;
  created_at: string;
  updated_at: string;
};

export type Task = {
  id: number;
  user_id: number;
  is_common: boolean;
  title: string;
  description: string;
  status: string;
  started_at: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
};

export type PromotionStatus = {
  status: "none" | "pending" | "approved";
  requested_at: string | null;
};

export type AutoApproveSettings = {
  auto_approve_promotions: boolean;
};

export type NewsItem = {
  id: number;
  title: string;
  summary: string;
  created_at: string;
};

export function login(identifier: string, password: string) {
  const isEmail = identifier.includes("@");
  const body = isEmail 
    ? { email: identifier, password }
    : { username: identifier, password };
    
  return request<{ user_id: number; full_name: string; role: string }>("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function logout() {
  return request<void>("/auth/logout", { method: "POST" });
}

export function me() {
  return request<User>("/auth/me", { method: "GET" });
}

export function getNews() {
  return request<NewsItem[]>("/home/news", { method: "GET" });
}

export function getLeaderboard() {
  return request<User[]>("/leaderboard", { method: "GET" });
}

export function getProfile(userId: string) {
  return request<User>(`/users/${userId}`, { method: "GET" });
}

export function getAssignableUsers() {
  return request<User[]>("/users/assignable", { method: "GET" });
}

export function getVisibleTasks() {
  return request<Task[]>("/tasks", { method: "GET" });
}

export function adminGetUsers() {
  return request<User[]>("/admin/users", { method: "GET" });
}

export function adminUpdateUserKpi(userId: number, kpi_score: number) {
  return request<User>(`/admin/users/${userId}/kpi`, {
    method: "PATCH",
    body: JSON.stringify({ kpi_score }),
  });
}

export function adminGetPendingPromotions() {
  return request<User[]>("/admin/promotions/pending", { method: "GET" });
}

export function adminApprovePromotion(userId: number) {
  return request<User>(`/admin/users/${userId}/promote`, { method: "POST" });
}

export function adminUpdateUserRole(userId: number, role: "junior_dev" | "senior_dev") {
  return request<User>(`/admin/users/${userId}/role`, {
    method: "PATCH",
    body: JSON.stringify({ role }),
  });
}

export function adminGetUserTasks(userId: number) {
  return request<Task[]>(`/admin/users/${userId}/tasks`, { method: "GET" });
}

export function adminGetReassignableTasks() {
  return request<Task[]>("/admin/tasks/reassignable", { method: "GET" });
}

export function adminAssignTask(taskId: number, userId: number) {
  return request<Task>(`/admin/tasks/${taskId}/assign`, {
    method: "PATCH",
    body: JSON.stringify({ user_id: userId }),
  });
}

export function adminGetAutoApprove() {
  return request<AutoApproveSettings>("/admin/settings/auto-approve", { method: "GET" });
}

export function adminSetAutoApprove(auto_approve_promotions: boolean) {
  return request<AutoApproveSettings>("/admin/settings/auto-approve", {
    method: "PATCH",
    body: JSON.stringify({ auto_approve_promotions }),
  });
}

export function startTask(taskId: number) {
  return request<{status: string}>(`/tasks/${taskId}/start`, { method: "POST" });
}

export function completeTask(taskId: number) {
  return request<{status: string, message: string}>(`/tasks/${taskId}/complete`, { method: "POST" });
}

export function requestPromotion() {
  return request<{message: string}>("/tasks/promotion", { method: "POST" });
}
