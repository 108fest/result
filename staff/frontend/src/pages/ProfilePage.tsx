import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getProfile, type User } from "../lib/api";

export function ProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [profile, setProfile] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setError("Missing user id");
      setLoading(false);
      return;
    }

    getProfile(id)
      .then((user) => setProfile(user))
      .catch(() => setError("Unable to load profile"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return <p>Loading...</p>;
  }

  if (error || !profile) {
    return <p className="error">{error ?? "Profile not found"}</p>;
  }

  return (
    <section>
      <h1>Employee Profile</h1>
      <div className="card profile-card">
        <img src={profile.photo_url} alt={profile.full_name} className="avatar" />
        <div>
          <h2>{profile.full_name}</h2>
          <p>Email: {profile.email}</p>
          <p>Role: {profile.role}</p>
          <p>KPI: {profile.kpi_score}</p>
        </div>
      </div>
    </section>
  );
}
