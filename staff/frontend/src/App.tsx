import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { LoginPage } from "./pages/LoginPage";
import { HomePage } from "./pages/HomePage";
import { LeaderboardPage } from "./pages/LeaderboardPage";
import { ProfilePage } from "./pages/ProfilePage";
import { AdminPage } from "./pages/AdminPage";
import { TasksPage } from "./pages/TasksPage";
import { EmailTemplatesPage } from "./pages/EmailTemplatesPage";
import { useAuth } from "./lib/auth";

function ProtectedRoutes() {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="page-center">Loading session...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
        <Route path="/tasks" element={<TasksPage />} />
        <Route path="/email-templates" element={user.level >= 1 ? <EmailTemplatesPage /> : <Navigate to="/" replace />} />
        <Route path="/profile/:id" element={<ProfilePage />} />
        <Route path="/admin" element={user.role === "admin" ? <AdminPage /> : <Navigate to="/" replace />} />
        <Route path="/me" element={<Navigate to={`/profile/${user.id}`} replace />} />
      </Routes>
    </AppLayout>
  );
}

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="*" element={<ProtectedRoutes />} />
    </Routes>
  );
}
