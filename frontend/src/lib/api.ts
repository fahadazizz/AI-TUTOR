// API Client for the AI Tutor Backend

const API_BASE = "http://127.0.0.1:8001/api";

export interface Student {
  student_id: string;
  name: string;
}

export interface Session {
  session_id: string;
  started_at: string;
}

export interface ChatResponse {
  action_taken: string;
  response: string;
}

export const api = {
  // 1. Register a new student (for demo purposes)
  register: async (name: string): Promise<Student> => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name,
        phone: "demo-" + Math.floor(Math.random() * 10000),
        class_level: 10,
        board: "punjab",
        group_type: "science",
        preferred_language: "ur",
      }),
    });
    
    if (!res.ok) throw new Error("Failed to register");
    return res.json();
  },

  // 2. Start a new session
  startSession: async (studentId: string): Promise<Session> => {
    const res = await fetch(`${API_BASE}/auth/start-session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, subject_key: "mathematics" }),
    });

    if (!res.ok) throw new Error("Failed to start session");
    return res.json();
  },

  // 3. Send a message to the tutor
  chat: async (sessionId: string, message: string): Promise<ChatResponse> => {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!res.ok) throw new Error("Failed to send message");
    return res.json();
  },

  // 4. Fetch the initial diagnostic assessment
  getAssessment: async () => {
    const res = await fetch(`${API_BASE}/curriculum/assessment`);
    if (!res.ok) throw new Error("Failed to fetch assessment");
    return res.json();
  },

  // 5. Fetch student mastery progress
  getProgress: async (studentId: string) => {
    const res = await fetch(`${API_BASE}/progress/${studentId}`);
    if (!res.ok) throw new Error("Failed to fetch progress");
    return res.json();
  }
};
