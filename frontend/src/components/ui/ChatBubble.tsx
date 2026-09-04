"use client";

import React from "react";
import styles from "./Chat.module.css";
// We import react-katex to render math safely
import { InlineMath, BlockMath } from 'react-katex';

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
  
  // Parse content to separate text from LaTeX blocks
  // For V1 we assume block math is wrapped in $$...$$ or \[...\] and inline in $...$
  const renderContent = (text: string) => {
    // Very basic parsing for demo (a real parser like remark-math would be better for prod)
    // For now, we'll just render everything as text, and use regex to find inline math `$x$`
    
    // Split by block math
    const blockParts = text.split(/\\\[([\s\S]*?)\\\]|\$\$([\s\S]*?)\$\$/g);
    
    return blockParts.map((part, i) => {
      if (!part) return null;
      
      // If it's a captured group from the regex, it's math
      if (i % 3 !== 0) {
        return (
          <div key={i} className={styles["math-block"]} dir="ltr">
            <BlockMath math={part} />
          </div>
        );
      }
      
      // Otherwise it's text that might contain inline math
      const inlineParts = part.split(/\$(.*?)\$/g);
      return (
        <span key={i}>
          {inlineParts.map((inlinePart, j) => {
            if (j % 2 !== 0) {
              return (
                <span key={j} className={styles["math-inline"]} dir="ltr">
                   <InlineMath math={inlinePart} />
                </span>
              );
            }
            return <span key={j}>{inlinePart}</span>;
          })}
        </span>
      );
    });
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
