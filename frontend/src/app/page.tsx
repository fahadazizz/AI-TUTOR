"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { BookOpen, ArrowRight } from "lucide-react";
import { api } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleStart = async () => {
    setIsLoading(true);
    try {
      // For V1, we auto-register a demo student and start a session
      const student = await api.register("Student (Demo)");
      const session = await api.startSession(student.student_id);
      
      // Save session info to localStorage so the chat page can use it
      localStorage.setItem("ai_tutor_session_id", session.session_id);
      
      router.push("/chat");
    } catch (error) {
      console.error(error);
      alert("Could not start session. Is the backend running?");
      setIsLoading(false);
    }
  };

  return (
    <main className="container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center" }}>
      <div className="glass-panel animate-fade-in" style={{ padding: "3rem", borderRadius: "var(--radius-lg)", textAlign: "center", maxWidth: "500px", width: "100%" }}>
        
        <div style={{ background: "var(--bg-tertiary)", width: "64px", height: "64px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
           <BookOpen size={32} color="var(--accent-primary)" />
        </div>
        
        <h1 style={{ marginBottom: "1rem", fontSize: "2rem" }}>AI Tutor</h1>
        <p style={{ color: "var(--text-secondary)", marginBottom: "2.5rem" }}>
          Welcome back. Ready to master some mathematics today?
        </p>
        
        <Button 
          variant="primary" 
          onClick={handleStart} 
          disabled={isLoading}
          style={{ width: "100%", padding: "1rem" }}
        >
          {isLoading ? "Starting Session..." : "Begin Session"} 
          {!isLoading && <ArrowRight size={20} />}
        </Button>
      </div>
    </main>
  );
}
