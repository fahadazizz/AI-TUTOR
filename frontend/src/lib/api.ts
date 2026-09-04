// API Client for the AI Tutor Backend

const API_BASE = "/api";

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

  // 3b. Send a message to the tutor (streaming)
  chatStream: async (
    sessionId: string, 
    message: string, 
    onToken: (token: string) => void,
    onMeta?: (meta: any) => void
  ): Promise<void> => {
    const res = await fetch(`${API_BASE}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!res.ok || !res.body) {
      throw new Error("Failed to start chat stream");
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        // Process lines in the buffer
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ""; // Keep the last incomplete chunk in the buffer
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.substring(6);
            if (dataStr === "[DONE]") {
              return;
            }
            try {
              const data = JSON.parse(dataStr);
              if (data.type === "token") {
                onToken(data.content);
              } else if (data.type === "meta" && onMeta) {
                onMeta(data);
              }
            } catch (e) {
              console.error("Failed to parse SSE JSON:", dataStr);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  // 4. Fetch the initial diagnostic assessment
  getAssessment: async () => {
    const res = await fetch(`${API_BASE}/curriculum/assessment`);
    if (!res.ok) throw new Error("Failed to fetch assessment");
    return res.json();
  },

  submitAssessment: async (studentId: string, answers: any[]) => {
    const res = await fetch(`${API_BASE}/curriculum/assessment/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, answers }),
    });
    if (!res.ok) throw new Error("Failed to submit assessment");
    return res.json();
  },

  // 5. Fetch student mastery progress
  getProgress: async (studentId: string) => {
    const res = await fetch(`${API_BASE}/progress/${studentId}`);
    if (!res.ok) throw new Error("Failed to fetch progress");
    return res.json();
  }
};
