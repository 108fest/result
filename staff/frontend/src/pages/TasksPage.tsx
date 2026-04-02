import { useEffect, useState } from "react";
import { getVisibleTasks, startTask, completeTask, requestPromotion, type Task } from "../lib/api";
import { useAuth } from "../lib/auth";

export function TasksPage() {
  const { user, refreshUser } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  async function loadTasks() {
    setLoading(true);
    setError(null);
    try {
      const data = await getVisibleTasks();
      setTasks(data);
    } catch {
      setError("Unable to load tasks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  async function handleStart(taskId: number) {
    setError(null);
    setMessage(null);
    try {
      await startTask(taskId);
      setMessage("Task started! Wait 1 minute to complete.");
      loadTasks();
    } catch (err: any) {
      setError(err.message || "Unable to start task");
    }
  }

  async function handleComplete(taskId: number) {
    setError(null);
    setMessage(null);
    try {
      const res = await completeTask(taskId);
      setMessage(res.message);
      loadTasks();
      refreshUser();
    } catch (err: any) {
      setError(err.message || "Unable to complete task");
    }
  }

  async function handlePromotion() {
    setError(null);
    setMessage(null);
    try {
      const res = await requestPromotion();
      setMessage(res.message);
    } catch (err: any) {
      setError(err.message || "Unable to request promotion");
    }
  }

  if (loading && tasks.length === 0) {
    return <p>Loading tasks...</p>;
  }

  return (
    <section style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ color: "var(--a-accent)" }}>My Tasks</h1>
      <p style={{ color: "var(--a-text-soft)" }}>Complete tasks to increase your KPI. Current KPI: <strong>{user?.kpi_score}</strong></p>
      
      {error && <div style={{ background: "var(--a-red)", color: "white", padding: "1rem", marginBottom: "1rem", borderRadius: "4px" }}>{error}</div>}
      {message && <div style={{ background: "var(--a-green)", color: "white", padding: "1rem", marginBottom: "1rem", borderRadius: "4px" }}>{message}</div>}

      <div style={{ marginBottom: "2rem" }}>
        <button 
          onClick={handlePromotion}
          style={{ background: "var(--a-yellow)", color: "black", fontWeight: "bold", padding: "0.75rem 1.5rem", border: "none", cursor: "pointer", borderRadius: "4px" }}
        >
          Request Promotion (Requires KPI &gt;= 10)
        </button>
      </div>

      <div className="card" style={{ background: "var(--a-bg-white)", border: "1px solid var(--a-line)", padding: "1.5rem" }}>
        <h2 style={{ marginTop: 0 }}>Available Tasks</h2>
        <p style={{ fontSize: "0.9rem", color: "var(--a-text-faint)" }}>Tasks refresh every 5 minutes. You can only complete tasks that have been in progress for at least 1 minute.</p>
        
        {tasks.length === 0 ? (
          <p>No tasks available right now.</p>
        ) : (
          <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "1rem" }}>
            {tasks.map((task) => (
              <li key={task.id} style={{ border: "1px solid var(--a-line)", padding: "1rem", borderRadius: "8px", background: "var(--a-bg-alt)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <h3 style={{ margin: "0 0 0.5rem 0", color: "var(--a-accent)" }}>{task.title}</h3>
                    <p style={{ margin: 0, color: "var(--a-text-soft)" }}>{task.description}</p>
                    <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.85rem", fontWeight: "bold", color: task.status === "completed" ? "var(--a-green)" : task.status === "in_progress" ? "var(--a-yellow)" : "var(--a-text-faint)" }}>
                      Status: {task.status.replace("_", " ").toUpperCase()}
                    </p>
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem", flexDirection: "column" }}>
                    {task.status === "pending" && (
                      <button 
                        onClick={() => handleStart(task.id)}
                        style={{ background: "var(--a-blue)", color: "white", border: "none", padding: "0.5rem 1rem", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Start Task
                      </button>
                    )}
                    {task.status === "in_progress" && (
                      <button 
                        onClick={() => handleComplete(task.id)}
                        style={{ background: "var(--a-green)", color: "white", border: "none", padding: "0.5rem 1rem", borderRadius: "4px", cursor: "pointer" }}
                      >
                        Complete Task
                      </button>
                    )}
                    {task.status === "completed" && (
                      <button disabled style={{ background: "var(--a-line-strong)", color: "var(--a-text-faint)", border: "none", padding: "0.5rem 1rem", borderRadius: "4px" }}>
                        Done
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
