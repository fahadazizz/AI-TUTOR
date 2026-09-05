"use client";

import React from "react";
import styles from "./Chat.module.css";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

// Visual Components
import { ParabolaGraph } from '../visuals/ParabolaGraph';
import { NumberLine } from '../visuals/NumberLine';
import { SystemGraph } from '../visuals/SystemGraph';
import { CompletingSquare } from '../visuals/CompletingSquare';
import { QuadraticFormula } from '../visuals/QuadraticFormula';
import { RootsNature } from '../visuals/RootsNature';
import { AreaModel } from '../visuals/AreaModel';
import { DependencyTree } from '../visuals/DependencyTree';

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
  const renderMarkdown = (text: string, index: number) => {
    return (
      <div key={`md-${index}`} className={styles["markdown-body"]}>
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkMath]} 
          rehypePlugins={[rehypeKatex]}
        >
          {text.replace(/\\\((.*?)\\\)/g, '$$$1$$').replace(/\\\[(.*?)\\\]/g, '$$$$$1$$$$')}
        </ReactMarkdown>
      </div>
    );
  };

  const renderVisual = (type: string, props: any, index: number) => {
    switch(type) {
      case 'parabola':
      case 'Parabola':
        return <ParabolaGraph key={`vis-${index}`} {...props} />;
      case 'numberline':
      case 'NumberLine':
        return <NumberLine key={`vis-${index}`} {...props} />;
      case 'system':
      case 'System':
        return <SystemGraph key={`vis-${index}`} {...props} />;
      case 'CompletingSquare':
        return <CompletingSquare key={`vis-${index}`} {...props} />;
      case 'QuadraticFormula':
        return <QuadraticFormula key={`vis-${index}`} {...props} />;
      case 'RootsNature':
        return <RootsNature key={`vis-${index}`} {...props} />;
      case 'AreaModel':
        return <AreaModel key={`vis-${index}`} {...props} />;
      case 'DependencyTree':
        return <DependencyTree key={`vis-${index}`} {...props} />;
      default:
        return <div key={`vis-${index}`} className="text-red-500 italic p-4 border border-red-500 rounded bg-slate-900">Unknown visual type: {type}</div>;
    }
  };

  const parseAndRender = (text: string) => {
    const regex = /(?:\$\$?)?\[(Graph|Diagram)\s+([^\]]+)\](?:\$\$?)?/g;
    let match;
    let lastIndex = 0;
    const elements = [];
    let idx = 0;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        elements.push(renderMarkdown(text.substring(lastIndex, match.index), idx++));
      }
      
      const attrsStr = match[2];
      const attrRegex = /([a-zA-Z0-9_]+)="([^"]*)"/g;
      const props: any = {};
      let attrMatch;
      while ((attrMatch = attrRegex.exec(attrsStr)) !== null) {
        props[attrMatch[1]] = isNaN(Number(attrMatch[2])) ? attrMatch[2] : Number(attrMatch[2]);
      }
      
      elements.push(renderVisual(props.type || props.Type, props, idx++));
      
      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      elements.push(renderMarkdown(text.substring(lastIndex), idx++));
    }

    return elements;
  };

  return (
    <div className={`${styles["bubble-wrapper"]} ${styles[role]} animate-fade-in`}>
      <div 
        className={`${styles.bubble} ${styles[role]} ${isUrdu ? `${styles.urdu} urdu-text` : ""}`}
        dir={isUrdu ? "rtl" : "ltr"}
      >
        {parseAndRender(content)}
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
