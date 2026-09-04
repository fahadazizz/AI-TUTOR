"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Send, CornerDownLeft, Superscript, Calculator, Divide, RefreshCcw } from "lucide-react";
import { api } from "@/lib/api";
import { ChatBubble, TypingIndicator } from "@/components/ui/ChatBubble";
import { Button } from "@/components/ui/Button";
import chatStyles from "@/components/ui/Chat.module.css";

interface Message {
  id: string;
  role: "student" | "tutor";
  content: string;
}

export default function ChatPage() {
  const router = useRouter();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [language, setLanguage] = useState("ur");
  const [studentId, setStudentId] = useState<string | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const id = localStorage.getItem("ai_tutor_session_id");
    if (!id) {
      router.push("/");
    } else {
      setSessionId(id);
      
      const sId = localStorage.getItem("ai_tutor_student_id");
      if (sId) setStudentId(sId);
    }
  }, [router]);

  // Trigger initial background message if chat is empty
  useEffect(() => {
    if (sessionId && messages.length === 0) {
      const initChat = async () => {
        setIsTyping(true);
        const tutorMsgId = crypto.randomUUID();
        setMessages([{ id: tutorMsgId, role: "tutor", content: "" }]);
        
        try {
          // Send a hidden "hello" to trigger the backend's greeting/continuation logic
          await api.chatStream(
            sessionId, 
            "Hello, let's start!",
            (token) => {
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === tutorMsgId 
                    ? { ...msg, content: msg.content + token }
                    : msg
                )
              );
            },
            (meta) => {
              console.log("Action taken on init:", meta.action_taken);
            }
          );
        } catch (error) {
          console.error(error);
          setMessages([{ id: tutorMsgId, role: "tutor", content: "Error connecting to server." }]);
        } finally {
          setIsTyping(false);
        }
      };
      
      initChat();
    }
  }, [sessionId, messages.length]);

  useEffect(() => {
    // Auto-scroll to bottom
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleLanguageChange = async (newLang: string) => {
    setLanguage(newLang);
    if (studentId) {
      try {
        await api.updateLanguage(studentId, newLang);
      } catch (err) {
        console.error("Failed to update language", err);
      }
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim() || !sessionId || isTyping) return;
    
    const studentMsg = inputValue.trim();
    setInputValue("");
    
    // Add student message to UI
    const newMsg: Message = { id: crypto.randomUUID(), role: "student", content: studentMsg };
    setMessages(prev => [...prev, newMsg]);
    setIsTyping(true);

    try {
      // Create empty placeholder message for tutor
      const tutorMsgId = crypto.randomUUID();
      setMessages(prev => [
        ...prev, 
        { id: tutorMsgId, role: "tutor", content: "" }
      ]);
      
      await api.chatStream(
        sessionId, 
        studentMsg,
        (token) => {
          setMessages(prev => 
            prev.map(msg => 
              msg.id === tutorMsgId 
                ? { ...msg, content: msg.content + token }
                : msg
            )
          );
        },
        (meta) => {
          console.log("Action taken:", meta.action_taken);
        }
      );
    } catch (error) {
      console.error(error);
      setMessages(prev => [
        ...prev, 
        { id: crypto.randomUUID(), role: "tutor", content: "Sorry, I am having trouble connecting to the server. Please try again." }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const insertMath = (symbol: string) => {
    setInputValue(prev => prev + symbol);
  };

  if (!sessionId) return null;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", maxWidth: "800px", margin: "0 auto" }}>
      
      {/* Header */}
      <header className="glass-panel" style={{ padding: "1rem", display: "flex", alignItems: "center", justifyContent: "space-between", borderBottom: "1px solid var(--bg-tertiary)", zIndex: 10 }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{ background: "var(--accent-primary)", width: "36px", height: "36px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Calculator size={18} color="#111" />
          </div>
          <div>
            <h2 style={{ fontSize: "1.1rem", fontWeight: 600 }}>Mathematics Tutor</h2>
            <div style={{ fontSize: "0.8rem", color: "var(--text-secondary)", display: "flex", alignItems: "center", gap: "0.3rem" }}>
               <span style={{ width: "8px", height: "8px", background: "var(--accent-primary)", borderRadius: "50%", display: "inline-block" }}></span>
               Active Session
            </div>
          </div>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <select 
            value={language} 
            onChange={(e) => handleLanguageChange(e.target.value)}
            style={{ 
              background: "var(--bg-tertiary)", 
              color: "var(--text-primary)", 
              border: "1px solid rgba(255,255,255,0.1)", 
              borderRadius: "var(--radius-sm)",
              padding: "0.4rem 0.75rem",
              fontSize: "0.85rem",
              outline: "none"
            }}
          >
            <option value="ur">🇵🇰 Urdu (Nastaliq)</option>
            <option value="roman_ur">💬 Roman Urdu</option>
            <option value="en">🇬🇧 English</option>
          </select>
          <Button variant="secondary" onClick={() => router.push("/progress")} style={{ padding: "0.5rem 1rem", fontSize: "0.85rem" }}>
            <Calculator size={14} /> Progress
          </Button>
          <Button variant="secondary" onClick={() => router.push("/")} style={{ padding: "0.5rem 1rem", fontSize: "0.85rem" }}>
            <RefreshCcw size={14} /> Reset
          </Button>
        </div>
      </header>

      {/* Chat Area */}
      <main style={{ flex: 1, overflow: "hidden", position: "relative" }}>
        <div className={chatStyles["chat-container"]} style={{ padding: "1.5rem" }}>
          {messages.map(msg => (
            <ChatBubble key={msg.id} role={msg.role} content={msg.content} />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={endOfMessagesRef} />
        </div>
      </main>

      {/* Input Area */}
      <footer className="glass-panel" style={{ padding: "1rem", borderTop: "1px solid var(--bg-tertiary)", zIndex: 10 }}>
        {/* Quick Math Tools */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem", overflowX: "auto", paddingBottom: "0.25rem" }}>
          <Button variant="secondary" iconOnly onClick={() => insertMath(" $x^2$ ")} title="Square">
             <Superscript size={16} color="var(--text-secondary)" />
          </Button>
          <Button variant="secondary" onClick={() => insertMath(" $\\sqrt{x}$ ")} style={{ padding: "0.25rem 0.75rem", fontSize: "0.9rem" }}>
             √x
          </Button>
          <Button variant="secondary" onClick={() => insertMath(" $\\frac{a}{b}$ ")} style={{ padding: "0.25rem 0.75rem", fontSize: "0.9rem" }}>
             <Divide size={16} />
          </Button>
          <Button variant="secondary" onClick={() => insertMath(" $\\pm$ ")} style={{ padding: "0.25rem 0.75rem", fontSize: "0.9rem" }}>
             ±
          </Button>
        </div>
        
        {/* Input Bar */}
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            style={{ 
              flex: 1, 
              background: "var(--bg-tertiary)", 
              border: "1px solid rgba(255,255,255,0.1)", 
              borderRadius: "var(--radius-md)", 
              padding: "0.75rem 1rem", 
              color: "var(--text-primary)",
              fontFamily: "inherit",
              resize: "none",
              minHeight: "48px",
              maxHeight: "120px",
              outline: "none"
            }}
            rows={1}
          />
          <Button 
             variant="primary" 
             onClick={handleSend} 
             disabled={!inputValue.trim() || isTyping}
             style={{ height: "48px", width: "48px", padding: 0 }}
             iconOnly
          >
            <Send size={20} />
          </Button>
        </div>
      </footer>
    </div>
  );
}
