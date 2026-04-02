import React, { useEffect, useRef, useState } from "react";
import { Link, Route, Routes, useParams, useNavigate } from "react-router-dom";

const API_BASE = (import.meta.env.VITE_API_BASE || "/api").replace(/\/$/, "");

function ChatsPage() {
  const [chats, setChats] = useState([]);
  const [me, setMe] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [joinJwt, setJoinJwt] = useState("");
  const [targetUserId, setTargetUserId] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError("");

      try {
        const meRes = await fetch(`${API_BASE}/me`, { credentials: "include" });
        if (meRes.ok) {
          setMe(await meRes.json());
        }

        const response = await fetch(`${API_BASE}/chats`, { credentials: "include" });
        if (response.status === 401) {
          setError("Unauthorized. Please login via Staff Portal first.");
          setChats([]);
          return;
        }
        if (!response.ok) {
          setError("Failed to load chats");
          setChats([]);
          return;
        }

        let loadedChats = await response.json();
        loadedChats = Array.isArray(loadedChats) ? loadedChats : [];

        // Load chats from localStorage JWTs
        const savedJwts = JSON.parse(localStorage.getItem("chat_jwts") || "{}");
        for (const [chatId, jwt] of Object.entries(savedJwts)) {
          // Ensure cookie is set
          document.cookie = `chat_access_${chatId}=${jwt}; path=/`;
          // Fetch meta
          try {
            const histRes = await fetch(`${API_BASE}/history/${chatId}`, { credentials: "include" });
            if (histRes.ok) {
              const histData = await histRes.json();
              if (histData.chat && !loadedChats.some(c => c.id === histData.chat.id)) {
                loadedChats.push(histData.chat);
              }
            }
          } catch (e) {}
        }

        setChats(loadedChats);
      } catch {
        setError("Cannot reach API");
        setChats([]);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const handleJoin = async (e) => {
    e.preventDefault();
    try {
      // Decode JWT payload to get chat_id
      const payloadBase64 = joinJwt.split('.')[1];
      if (!payloadBase64) throw new Error("Invalid JWT format");
      
      const payload = JSON.parse(atob(payloadBase64));
      const chatId = payload.chat_id;
      if (!chatId) throw new Error("JWT missing chat_id");

      // Set cookie directly
      document.cookie = `chat_access_${chatId}=${joinJwt}; path=/`;

      const savedJwts = JSON.parse(localStorage.getItem("chat_jwts") || "{}");
      savedJwts[chatId] = joinJwt;
      localStorage.setItem("chat_jwts", JSON.stringify(savedJwts));
      
      navigate(`/${chatId}`);
    } catch (err) {
      setError("Error joining chat: " + err.message);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`${API_BASE}/chats/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_user_id: targetUserId }),
        credentials: "include"
      });
      const data = await res.json();
      if (res.ok) {
        // Set cookie directly
        document.cookie = `chat_access_${data.chat_id}=${data.jwt}; path=/`;

        const savedJwts = JSON.parse(localStorage.getItem("chat_jwts") || "{}");
        savedJwts[data.chat_id] = data.jwt;
        localStorage.setItem("chat_jwts", JSON.stringify(savedJwts));
        
        navigate(`/${data.chat_id}`);
      } else {
        setError(data.detail || "Failed to create");
      }
    } catch (err) {
      setError("Error creating chat");
    }
  };

  return (
    <div className="main-container">
      <header className="topbar" style={{ marginBottom: "2rem" }}>
        <div className="brand">Astra Messenger</div>
        {me && <div>Logged in as: <strong>{me.username}</strong></div>}
      </header>

      {loading && <p>Loading...</p>}
      {!loading && error && <div className="error card">{error}</div>}

      {!loading && !error && (
        <div className="grid">
          <div className="card">
            <h2>Your Chats</h2>
            {chats.length === 0 ? (
              <p className="text-soft">No chats found.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {chats.map((chat) => {
                  const title = chat.other_user?.username || chat.title || `Chat #${chat.id}`;
                  return (
                    <li key={chat.id} style={{ padding: "1rem", border: "1px solid var(--a-line)", borderRadius: "4px", background: "var(--a-bg-alt)" }}>
                      <Link to={`/${chat.id}`} style={{ fontWeight: "bold", color: "var(--a-accent)" }}>
                        {title}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div className="card">
              <h2>Join Chat</h2>
              <form onSubmit={handleJoin} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <textarea 
                  placeholder="Paste Chat Access JWT here..." 
                  value={joinJwt} 
                  onChange={e => setJoinJwt(e.target.value)}
                  rows={4}
                  required
                />
                <button type="submit">Join via JWT</button>
              </form>
            </div>

            {me?.level >= 1 && (
              <div className="card" style={{ border: "2px solid var(--a-accent)" }}>
                <h2>Create Chat (Senior+)</h2>
                <form onSubmit={handleCreate} style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                  <input 
                    type="number" 
                    placeholder="Target User ID" 
                    value={targetUserId} 
                    onChange={e => setTargetUserId(e.target.value)}
                    required
                  />
                  <button type="submit" style={{ background: "var(--a-red)" }}>Create New Chat</button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function ChatHistoryPage() {
  const { chatId } = useParams();
  const [messages, setMessages] = useState([]);
  const [chatMeta, setChatMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [draftMessage, setDraftMessage] = useState("");
  const [socketReady, setSocketReady] = useState(false);
  const [typing, setTyping] = useState(false);
  const socketRef = useRef(null);

  useEffect(() => {
    async function loadMessages() {
      setLoading(true);
      setError("");

      try {
        const response = await fetch(`${API_BASE}/history/${chatId}`, {
          credentials: "include"
        });

        if (response.status === 401) {
          setError("Unauthorized");
          return;
        }
        if (response.status === 403) {
          setError("Access Denied. You need a valid JWT to join this chat.");
          return;
        }
        if (!response.ok) {
          setError("Failed to load history");
          return;
        }

        const data = await response.json();
        setChatMeta(data?.chat || null);
        setMessages(Array.isArray(data?.messages) ? data.messages : []);
      } catch {
        setError("Cannot reach API");
      } finally {
        setLoading(false);
      }
    }

    loadMessages();
  }, [chatId]);

  useEffect(() => {
    if (!chatMeta?.current_user?.id) return;

    const socketProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${socketProtocol}//${window.location.host}${API_BASE}/ws/${chatId}`);
    socketRef.current = socket;

    socket.onopen = () => setSocketReady(true);
    
    socket.onmessage = (event) => {
      try {
        const incoming = JSON.parse(event.data);
        if (incoming && incoming.typing && incoming.sender_id === chatMeta?.other_user?.id) {
          setTyping(true);
          setTimeout(() => setTyping(false), 2500);
          return;
        }
        setMessages((currentMessages) => {
          if (currentMessages.some((m) => m.id === incoming.id)) return currentMessages;
          return [...currentMessages, incoming];
        });
      } catch {}
    };

    socket.onclose = () => setSocketReady(false);
    socket.onerror = () => setSocketReady(false);

    return () => {
      socket.close();
      socketRef.current = null;
      setSocketReady(false);
    };
  }, [chatId, chatMeta?.current_user?.id]);

  function sendMessage(e) {
    e.preventDefault();
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) return;
    
    const content = draftMessage.trim();
    if (!content || !chatMeta?.current_user?.id) return;

    socketRef.current.send(JSON.stringify({
      sender_id: chatMeta.current_user.id,
      message_text: content
    }));
    setDraftMessage("");
  }

  return (
    <div className="main-container">
      <header className="topbar" style={{ marginBottom: "2rem" }}>
        <div className="brand">Astra Messenger</div>
        <Link to="/" style={{ fontWeight: "bold" }}>&larr; Back to Chats</Link>
      </header>

      {loading && <p>Loading...</p>}
      {!loading && error && <div className="error card">{error}</div>}

      {!loading && !error && (
        <div className="card" style={{ display: "flex", flexDirection: "column", height: "600px" }}>
          <h2 style={{ borderBottom: "1px solid var(--a-line)", paddingBottom: "1rem", margin: "0 0 1rem 0" }}>
            {chatMeta?.other_user?.username || chatMeta?.title || `Chat ${chatId}`}
          </h2>
          
          <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem", padding: "1rem", background: "var(--a-bg-alt)", borderRadius: "4px" }}>
            {messages.length === 0 ? (
              <p className="text-soft" style={{ textAlign: "center", marginTop: "2rem" }}>No messages yet.</p>
            ) : (
              messages.map((msg) => {
                const isMine = msg.sender_id === chatMeta?.current_user?.id;
                return (
                  <div key={msg.id} style={{ alignSelf: isMine ? "flex-end" : "flex-start", maxWidth: "70%" }}>
                    <div style={{ fontSize: "0.8rem", color: "var(--a-text-soft)", marginBottom: "0.25rem", textAlign: isMine ? "right" : "left" }}>
                      {msg.sender?.username}
                    </div>
                    <div style={{ 
                      background: isMine ? "var(--a-accent)" : "var(--a-bg-white)", 
                      color: isMine ? "white" : "var(--a-text)",
                      padding: "0.75rem 1rem", 
                      borderRadius: "8px",
                      border: isMine ? "none" : "1px solid var(--a-line)"
                    }}>
                      {msg.message_text}
                    </div>
                  </div>
                );
              })
            )}
            {typing && (
              <div style={{ alignSelf: "flex-start", maxWidth: "70%" }}>
                <div style={{ fontSize: "0.8rem", color: "var(--a-text-soft)", marginBottom: "0.25rem" }}>
                  {chatMeta?.other_user?.username || "Admin"}
                </div>
                <div style={{ background: "var(--a-bg-white)", padding: "0.75rem 1rem", borderRadius: "8px", border: "1px solid var(--a-line)" }}>
                  <span style={{ color: "var(--a-text-faint)", fontStyle: "italic" }}>typing...</span>
                </div>
              </div>
            )}
          </div>

          <form onSubmit={sendMessage} style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
            <input
              style={{ flex: 1 }}
              value={draftMessage}
              onChange={(e) => setDraftMessage(e.target.value)}
              placeholder={socketReady ? "Type a message..." : "Connecting..."}
              disabled={!socketReady}
            />
            <button type="submit" disabled={!socketReady || !draftMessage.trim()}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ChatsPage />} />
      <Route path="/:chatId" element={<ChatHistoryPage />} />
    </Routes>
  );
}
