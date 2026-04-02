import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  adminAssignTask,
  adminApprovePromotion,
  adminGetAutoApprove,
  adminGetPendingPromotions,
  adminGetReassignableTasks,
  adminGetUserTasks,
  adminUpdateUserRole,
  adminGetUsers,
  adminSetAutoApprove,
  adminUpdateUserKpi,
  type Task,
  type User,
} from "../lib/api";

type KpiDraft = Record<number, string>;
type TasksByUser = Record<number, Task[]>;
type TaskAssigneeDraft = Record<number, string>;
type KpiPopupState = { id: number; text: string } | null;

export function AdminPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [pendingUsers, setPendingUsers] = useState<User[]>([]);
  const [tasksByUser, setTasksByUser] = useState<TasksByUser>({});
  const [kpiDraft, setKpiDraft] = useState<KpiDraft>({});
  const [taskAssigneeDraft, setTaskAssigneeDraft] = useState<TaskAssigneeDraft>({});
  const [reassignableTasks, setReassignableTasks] = useState<Task[]>([]);
  const [autoApprove, setAutoApprove] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [kpiPopup, setKpiPopup] = useState<KpiPopupState>(null);

  const sortedUsers = useMemo(() => [...users].sort((a, b) => a.id - b.id), [users]);

  async function loadAdminData() {
    setLoading(true);
    setError(null);
    try {
      const [usersData, pendingData, autoApproveData, reassignableData] = await Promise.all([
        adminGetUsers(),
        adminGetPendingPromotions(),
        adminGetAutoApprove(),
        adminGetReassignableTasks(),
      ]);

      setUsers(usersData);
      setPendingUsers(pendingData);
      setAutoApprove(autoApproveData.auto_approve_promotions);
      setReassignableTasks(reassignableData);
      setKpiDraft((prev) => {
        const next: KpiDraft = { ...prev };
        usersData.forEach((user) => {
          if (!(user.id in next)) {
            next[user.id] = String(user.kpi_score);
          }
        });
        return next;
      });

      const tasksEntries = await Promise.all(
        usersData.map(async (user) => [user.id, await adminGetUserTasks(user.id)] as const)
      );
      const nextTasksByUser = Object.fromEntries(tasksEntries);
      setTasksByUser(nextTasksByUser);
      setTaskAssigneeDraft((prev) => {
        const next: TaskAssigneeDraft = { ...prev };
        Object.values(nextTasksByUser)
          .flat()
          .forEach((task) => {
            if (!(task.id in next)) {
              next[task.id] = String(task.user_id);
            }
          });
        reassignableData.forEach((task) => {
          if (!(task.id in next)) {
            next[task.id] = String(task.user_id);
          }
        });
        return next;
      });
    } catch {
      setError("Unable to load admin data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAdminData();
  }, []);

  async function handleKpiSubmit(event: FormEvent<HTMLFormElement>, userId: number) {
    event.preventDefault();
    const nextKpi = Number(kpiDraft[userId] ?? "0");
    if (Number.isNaN(nextKpi) || nextKpi < 0) {
      setError("KPI must be a non-negative number");
      return;
    }

    setKpiPopup(null);
    try {
      const previous = users.find((user) => user.id === userId)?.kpi_score ?? 0;
      const updated = await adminUpdateUserKpi(userId, nextKpi);
      setUsers((prev) => prev.map((user) => (user.id === updated.id ? updated : user)));
      setMessage(`KPI updated for user #${updated.id}`);
      const direction = nextKpi > previous ? "increased" : nextKpi < previous ? "decreased" : "kept unchanged";
      setKpiPopup({ id: Date.now(), text: `KPI ${direction} for ${updated.full_name}: ${previous} -> ${updated.kpi_score}` });
    } catch {
      setError("Failed to update KPI");
    }
  }

  async function handleApprove(userId: number) {
    try {
      await adminApprovePromotion(userId);
      setMessage(`Promotion approved for user #${userId}`);
      await loadAdminData();
    } catch {
      setError("Failed to approve promotion");
    }
  }

  async function handleRoleChange(userId: number, role: "junior_dev" | "senior_dev") {
    try {
      const updated = await adminUpdateUserRole(userId, role);
      setUsers((prev) => prev.map((user) => (user.id === updated.id ? updated : user)));
      setPendingUsers((prev) => prev.filter((user) => user.id !== updated.id));
      setMessage(`Role updated for ${updated.full_name}`);
    } catch {
      setError("Failed to update user role");
    }
  }

  async function handleTaskAssign(taskId: number) {
    const targetUserId = Number(taskAssigneeDraft[taskId] ?? "0");
    if (!targetUserId) {
      setError("Select user for task assignment");
      return;
    }

    try {
      await adminAssignTask(taskId, targetUserId);
      setMessage(`Task #${taskId} reassigned`);
      await loadAdminData();
    } catch {
      setError("Failed to reassign task");
    }
  }

  const assignableUsers = users.filter(
    (user) => user.role === "admin" || user.role === "junior_dev" || user.role === "senior_dev"
  );

  async function handleAutoApproveChange(enabled: boolean) {
    try {
      const result = await adminSetAutoApprove(enabled);
      setAutoApprove(result.auto_approve_promotions);
      setMessage(`Auto approve ${result.auto_approve_promotions ? "enabled" : "disabled"}`);
    } catch {
      setError("Failed to update auto-approve setting");
    }
  }

  if (loading) {
    return <p>Loading admin panel...</p>;
  }

  return (
    <section>
      <h1>Admin Panel</h1>
      <p>Manage KPI, tasks and promotion requests.</p>

      {error && <p className="error">{error}</p>}
      {message && <p>{message}</p>}

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Promotion Settings</h2>
        <label style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <input
            type="checkbox"
            checked={autoApprove}
            onChange={(event) => handleAutoApproveChange(event.target.checked)}
          />
          Auto approve promotions for users with KPI &gt;= 100
        </label>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>Pending Promotions</h2>
        {pendingUsers.length === 0 ? (
          <p>No pending requests.</p>
        ) : (
          <ul>
            {pendingUsers.map((user) => (
              <li key={user.id} style={{ marginBottom: 8 }}>
                {user.full_name} ({user.email}) - Role: {user.role} - KPI: {user.kpi_score}
                <button type="button" onClick={() => handleApprove(user.id)} style={{ marginLeft: 10 }}>
                  Approve to Senior
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h2>All Unfinished Tasks</h2>
        {reassignableTasks.length === 0 ? (
          <p>No unfinished tasks.</p>
        ) : (
          <ul>
            {reassignableTasks.map((task) => (
              <li key={task.id} style={{ marginBottom: 8 }}>
                #{task.id} {task.title}
                <span style={{ marginLeft: 8 }}>
                  <select
                    value={taskAssigneeDraft[task.id] ?? String(task.user_id)}
                    onChange={(event) => setTaskAssigneeDraft((prev) => ({ ...prev, [task.id]: event.target.value }))}
                  >
                    {assignableUsers.map((assignableUser) => (
                      <option key={assignableUser.id} value={assignableUser.id}>
                        {assignableUser.full_name} ({assignableUser.role})
                      </option>
                    ))}
                  </select>
                  <button type="button" onClick={() => handleTaskAssign(task.id)} style={{ marginLeft: 6 }}>
                    Reassign
                  </button>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h2>Users</h2>
        {sortedUsers.map((user) => (
          <div key={user.id} style={{ borderTop: "1px solid #e2ddd6", padding: "12px 0" }}>
            <h3 style={{ marginBottom: 6 }}>
              {user.full_name} ({user.role})
            </h3>
            <p style={{ marginBottom: 8 }}>{user.email}</p>
            <p style={{ marginBottom: 8 }}>
              Current Role: <strong>{user.role}</strong>
            </p>

            {user.role !== "admin" && (
              <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
                <button type="button" onClick={() => handleRoleChange(user.id, "junior_dev")}>
                  Set Junior
                </button>
                <button type="button" onClick={() => handleRoleChange(user.id, "senior_dev")}>
                  Set Senior
                </button>
              </div>
            )}

            <form onSubmit={(event) => handleKpiSubmit(event, user.id)} style={{ display: "flex", gap: 8 }}>
              <input
                type="number"
                min={0}
                value={kpiDraft[user.id] ?? String(user.kpi_score)}
                onChange={(event) => setKpiDraft((prev) => ({ ...prev, [user.id]: event.target.value }))}
              />
              <button type="submit">Update KPI</button>
            </form>

            <div style={{ marginTop: 10 }}>
              <strong>Tasks:</strong>
              <ul>
                {(tasksByUser[user.id] ?? []).map((task) => (
                  <li key={task.id} style={{ marginBottom: 6 }}>
                    [{task.is_completed ? "x" : " "}] {task.title}
                    {!task.is_completed && (
                      <span style={{ marginLeft: 8 }}>
                        <select
                          value={taskAssigneeDraft[task.id] ?? String(task.user_id)}
                          onChange={(event) =>
                            setTaskAssigneeDraft((prev) => ({ ...prev, [task.id]: event.target.value }))
                          }
                        >
                          {assignableUsers.map((assignableUser) => (
                            <option key={assignableUser.id} value={assignableUser.id}>
                              {assignableUser.full_name} ({assignableUser.role})
                            </option>
                          ))}
                        </select>
                        <button type="button" onClick={() => handleTaskAssign(task.id)} style={{ marginLeft: 6 }}>
                          Reassign
                        </button>
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>

      {kpiPopup && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal-card" key={kpiPopup.id}>
            <h3>KPI Updated</h3>
            <p>{kpiPopup.text}</p>
            <button type="button" onClick={() => setKpiPopup(null)}>
              OK
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
