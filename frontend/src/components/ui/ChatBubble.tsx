"use client";

import React from "react";
import styles from "./Chat.module.css";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

interface ChatBubbleProps {
  role: "student" | "tutor";
  content: string;
}

// Simple heuristic: if the text contains Urdu/Arabic characters, treat as Urdu
const containsUrdu = (text: string) => {
  const urduRegex = /[\u0600-\u06FF]/;
  return urduRegex.test(text);
};

export const ChatBubble: React.FC<ChatBubbleProps> = ({ role, content }) => {
  const isUrdu = role === "tutor" && containsUrdu(content);
  
  // Use ReactMarkdown to render the content with tables and math support
  const renderContent = (text: string) => {
    return (
      <div className={styles["markdown-body"]}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkMath]} 
          rehypePlugins={[rehypeKatex]}
        >
          {text}
        </ReactMarkdown>
      </div>
    );
  };

  return (
    <div className={`${styles["bubble-wrapper"]} ${styles[role]} animate-fade-in`}>
      <div 
        className={`${styles.bubble} ${styles[role]} ${isUrdu ? `${styles.urdu} urdu-text` : ""}`}
        dir={isUrdu ? "rtl" : "ltr"}
      >
        {renderContent(content)}
      </div>
    </div>
  );
};

export const TypingIndicator = () => (
  <div className={`${styles["bubble-wrapper"]} ${styles.tutor} animate-fade-in`}>
    <div className={`${styles.bubble} ${styles.tutor}`}>
      <div className={styles["typing-indicator"]}>
        <div className={styles.dot}></div>
        <div className={styles.dot}></div>
        <div className={styles.dot}></div>
      </div>
    </div>
  </div>
);
