import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getLeaderboard, type User } from "../lib/api";

export function LeaderboardPage() {
  const [rows, setRows] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLeaderboard()
      .then((items) => setRows(items))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section>
      <h1>KPI Leaderboard</h1>
      {loading && <p>Loading...</p>}
      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Employee</th>
              <th>Email</th>
              <th>KPI</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((user, index) => (
              <tr key={user.id}>
                <td>{index + 1}</td>
                <td>
                  <Link to={`/profile/${user.id}`}>{user.full_name}</Link>
                </td>
                <td>{user.email}</td>
                <td>{user.kpi_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
