import { useState } from "react";
import { useAuth } from "../lib/auth";

const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export function EmailTemplatesPage() {
  const { user } = useAuth();
  const [template, setTemplate] = useState("");
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handlePreview(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setPreview("");

    try {
      const response = await fetch(`${API_BASE_URL}/email_templates/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ template }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Failed to preview template");
      } else if (data.error) {
        setError(data.error);
      } else {
        setPreview(data.rendered);
      }
    } catch (err) {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h1 style={{ color: "var(--a-accent)" }}>Email Templates (Beta)</h1>
      <p style={{ color: "var(--a-text-soft)" }}>
        Test our new dynamic email templating engine. 
        Note: This feature is currently in beta and only available for testing.
      </p>

      <div className="card" style={{ background: "var(--a-bg-white)", border: "1px solid var(--a-line)", padding: "1.5rem", marginBottom: "2rem" }}>
        <form onSubmit={handlePreview} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <label style={{ fontWeight: "bold" }}>Template Content:</label>
          <textarea
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            rows={10}
            placeholder="Dear {{ user.name }}, welcome to Astra Technologies..."
            style={{ width: "100%", padding: "0.75rem", fontFamily: "monospace", border: "1px solid var(--a-line-strong)", borderRadius: "4px" }}
            required
          />
          <button 
            type="submit" 
            disabled={loading}
            style={{ background: "var(--a-blue)", color: "white", padding: "0.75rem", border: "none", borderRadius: "4px", cursor: loading ? "not-allowed" : "pointer", fontWeight: "bold" }}
          >
            {loading ? "Rendering..." : "Preview Template"}
          </button>
        </form>
      </div>

      {error && (
        <div style={{ background: "var(--a-red)", color: "white", padding: "1rem", borderRadius: "4px", marginBottom: "2rem" }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {preview && (
        <div className="card" style={{ background: "var(--a-bg-alt)", border: "1px dashed var(--a-line-strong)", padding: "1.5rem" }}>
          <h3 style={{ marginTop: 0, color: "var(--a-accent)" }}>Preview Result:</h3>
          <div style={{ whiteSpace: "pre-wrap", fontFamily: "monospace", background: "var(--a-bg-white)", padding: "1rem", border: "1px solid var(--a-line)" }}>
            {preview}
          </div>
        </div>
      )}
    </section>
  );
}
