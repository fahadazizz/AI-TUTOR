"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { ChatBubble } from "@/components/ui/ChatBubble";

export default function AssessmentPage() {
  const router = useRouter();
  const [questions, setQuestions] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [inputValue, setInputValue] = useState("");
  const [isComplete, setIsComplete] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchQuestions = async () => {
      try {
        const data = await api.getAssessment();
        setQuestions(data.questions || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchQuestions();
  }, []);

  const [answers, setAnswers] = useState<any[]>([]);

  const handleNext = async () => {
    if (!inputValue.trim()) return;

    const currentQ = questions[currentIndex];
    const newAnswers = [
      ...answers,
      {
        question_id: currentQ.question_id,
        concept_id: currentQ.concept_id,
        student_answer: inputValue.trim()
      }
    ];
    setAnswers(newAnswers);
    setInputValue("");

    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    } else {
      setLoading(true);
      try {
        const studentId = localStorage.getItem("ai_tutor_student_id");
        if (studentId) {
          await api.submitAssessment(studentId, newAnswers);
        }
      } catch (err) {
        console.error("Failed to submit assessment:", err);
      } finally {
        setLoading(false);
        setIsComplete(true);
      }
    }
  };

  const finishAssessment = () => {
    router.push("/chat");
  };

  if (loading) {
    return (
      <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
        <p>Loading assessment...</p>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
        <p>No questions available.</p>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="container" style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
        <div className="glass-panel" style={{ padding: "3rem", textAlign: "center", borderRadius: "var(--radius-lg)" }}>
          <h2 style={{ marginBottom: "1rem", fontSize: "1.8rem" }}>Assessment Complete!</h2>
          <p style={{ color: "var(--text-secondary)", marginBottom: "2rem" }}>
            We've customized your learning path based on your results.
          </p>
          <Button variant="primary" onClick={finishAssessment}>
            Start Tutoring Session
          </Button>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIndex];

  return (
    <div className="container" style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: "800px", margin: "0 auto", padding: "2rem" }}>
      
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.5rem" }}>Diagnostic Assessment</h1>
        <span style={{ color: "var(--text-secondary)" }}>
          Question {currentIndex + 1} of {questions.length}
        </span>
      </header>

      {/* Progress Bar */}
      <div style={{ width: "100%", height: "4px", background: "var(--bg-tertiary)", borderRadius: "2px", marginBottom: "3rem" }}>
        <div 
          style={{ 
            height: "100%", 
            background: "var(--accent-primary)", 
            borderRadius: "2px", 
            width: `${((currentIndex) / questions.length) * 100}%`,
            transition: "width 0.3s ease"
          }} 
        />
      </div>

      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* Render question using ChatBubble for KaTeX/Urdu support */}
        <ChatBubble role="tutor" content={currentQ.question_text_ur || currentQ.question_text_en} />
        
        <div style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
          <input 
            type="text" 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your answer here..."
            style={{ 
              flex: 1, 
              background: "var(--bg-tertiary)", 
              border: "1px solid rgba(255,255,255,0.1)", 
              borderRadius: "var(--radius-md)", 
              padding: "1rem", 
              color: "var(--text-primary)",
              fontFamily: "inherit",
              outline: "none",
              fontSize: "1.1rem"
            }}
            onKeyDown={(e) => e.key === "Enter" && inputValue.trim() && handleNext()}
          />
          <Button 
             variant="primary" 
             onClick={handleNext} 
             disabled={!inputValue.trim()}
             style={{ padding: "0 2rem" }}
          >
            {currentIndex === questions.length - 1 ? "Finish" : "Next"}
          </Button>
        </div>
      </main>
      
    </div>
  );
}
