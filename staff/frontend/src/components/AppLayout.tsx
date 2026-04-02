import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../lib/auth";

export function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Staff Portal</div>
        <nav>
          <Link to="/">News</Link>
          <Link to="/leaderboard">KPI Leaderboard</Link>
          <Link to="/tasks">Tasks</Link>
          {user && user.level >= 1 && <Link to="/email-templates">Email Templates</Link>}
          {user && <Link to={`/profile/${user.id}`}>My Profile</Link>}
          {user?.role === "admin" && <Link to="/admin">Admin Panel</Link>}
        </nav>
        <div className="topbar-right">
          {user && <span className="role-chip">{user.role}</span>}
        <button
          type="button"
          className="ghost"
          onClick={async () => {
            await logout();
            navigate("/login", { replace: true });
          }}
        >
          Logout
        </button>
        </div>
      </header>
      <main className="main-container">{children}</main>
    </div>
  );
}
