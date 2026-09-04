"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ArrowLeft, BookOpen, CheckCircle, Clock, AlertTriangle } from "lucide-react";

export default function ProgressPage() {
  const router = useRouter();
  const [masteryData, setMasteryData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const studentId = localStorage.getItem("ai_tutor_student_id");
    if (!studentId) {
      router.push("/");
      return;
    }

    const fetchProgress = async () => {
      try {
        const data = await api.getProgress(studentId);
        setMasteryData(data.mastery || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, [router]);

  const getStatusColor = (level: string) => {
    switch (level) {
      case "MASTERED": return "var(--accent-primary)"; // Sage green
      case "PRACTICING": return "#D9A05B"; // Muted yellow/gold
      case "STRUGGLING": return "#C45B5B"; // Muted rose
      default: return "var(--text-secondary)"; // Gray
    }
  };

  const getStatusIcon = (level: string) => {
    switch (level) {
      case "MASTERED": return <CheckCircle size={18} color="var(--accent-primary)" />;
      case "PRACTICING": return <Clock size={18} color="#D9A05B" />;
      case "STRUGGLING": return <AlertTriangle size={18} color="#C45B5B" />;
      default: return <BookOpen size={18} color="var(--text-secondary)" />;
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      
      <header style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "3rem" }}>
        <Button variant="secondary" iconOnly onClick={() => router.push("/chat")}>
           <ArrowLeft size={20} />
        </Button>
        <h1 style={{ fontSize: "1.8rem" }}>Mastery Progress</h1>
      </header>

      {loading ? (
        <div style={{ display: "flex", flex: 1, alignItems: "center", justifyContent: "center" }}>
          <p>Loading your progress...</p>
        </div>
      ) : (
        <main style={{ flex: 1, overflowY: "auto", display: "grid", gap: "1rem" }}>
          {masteryData.length === 0 ? (
            <div className="glass-panel" style={{ padding: "2rem", textAlign: "center" }}>
              <p>No progress data yet. Complete your assessment to begin!</p>
            </div>
          ) : (
            masteryData.map((item, idx) => (
              <div 
                key={idx}
                className="glass-panel animate-fade-in"
                style={{ 
                  padding: "1.5rem", 
                  display: "flex", 
                  justifyContent: "space-between", 
                  alignItems: "center",
                  borderLeft: `4px solid ${getStatusColor(item.mastery_level)}`
                }}
              >
                <div>
                  <h3 style={{ fontSize: "1.1rem", marginBottom: "0.25rem" }}>
                    {item.concept_id.split('.').pop()?.replace(/_/g, ' ')}
                  </h3>
                  <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: "0.5rem" }}>
                    {getStatusIcon(item.mastery_level)}
                    <span style={{ textTransform: "capitalize" }}>{item.mastery_level.toLowerCase()}</span>
                  </div>
                </div>
                
                <div style={{ textAlign: "right", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                  <div>Attempts: {item.attempts}</div>
                  <div>Mistakes: {item.mistakes}</div>
                </div>
              </div>
            ))
          )}
        </main>
      )}
    </div>
  );
}
