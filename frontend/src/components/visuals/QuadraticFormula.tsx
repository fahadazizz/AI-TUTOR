import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

interface QuadraticFormulaProps {
  a: number;
  b: number;
  c: number;
}

export const QuadraticFormula: React.FC<QuadraticFormulaProps> = ({ a, b, c }) => {
  // Let's use HTML/CSS to build a visual breakdown. 
  // SVG with KaTeX is hard because KaTeX outputs HTML. 
  // But we can just use styled divs that look like a diagram!

  const b_str = b < 0 ? `(${b})` : `${b}`;
  const a_str = a < 0 ? `(${a})` : `${a}`;
  const c_str = c < 0 ? `(${c})` : `${c}`;

  return (
    <div style={{ margin: '1.5rem 0', display: 'flex', justifyContent: 'center', width: '100%' }}>
      <div style={{ 
        backgroundColor: '#1e293b', 
        borderRadius: '0.75rem', 
        padding: '2rem', 
        border: '1px solid #334155', 
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '1.5rem'
      }}>
        <div style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          Quadratic Formula Substitution
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', fontSize: '1.5rem', fontFamily: 'serif' }}>
          <span style={{ color: '#f8fafc', marginRight: '1rem' }}>x = </span>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', paddingBottom: '0.25rem', borderBottom: '2px solid #94a3b8' }}>
              <span style={{ color: '#f8fafc' }}>-</span>
              <span style={{ color: '#3b82f6', margin: '0 0.25rem', fontWeight: 'bold' }}>{b_str}</span>
              <span style={{ color: '#f8fafc', margin: '0 0.5rem' }}>±</span>
              <span style={{ color: '#f8fafc' }}>√</span>
              <span style={{ borderTop: '2px solid #f8fafc', display: 'flex', alignItems: 'center', padding: '0.1rem 0.25rem' }}>
                <span style={{ color: '#3b82f6', fontWeight: 'bold' }}>{b_str}</span>
                <sup style={{ color: '#f8fafc', fontSize: '0.8em' }}>2</sup>
                <span style={{ color: '#f8fafc', margin: '0 0.25rem' }}>- 4</span>
                <span style={{ color: '#10b981', fontWeight: 'bold' }}>{a_str}</span>
                <span style={{ color: '#f59e0b', fontWeight: 'bold' }}>{c_str}</span>
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', paddingTop: '0.25rem' }}>
              <span style={{ color: '#f8fafc' }}>2</span>
              <span style={{ color: '#10b981', fontWeight: 'bold', marginLeft: '0.25rem' }}>{a_str}</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '2rem', marginTop: '1rem', fontSize: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#10b981', borderRadius: '50%' }}></span>
            <span style={{ color: '#94a3b8' }}>a = {a}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#3b82f6', borderRadius: '50%' }}></span>
            <span style={{ color: '#94a3b8' }}>b = {b}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ display: 'inline-block', width: '12px', height: '12px', backgroundColor: '#f59e0b', borderRadius: '50%' }}></span>
            <span style={{ color: '#94a3b8' }}>c = {c}</span>
          </div>
        </div>

      </div>
    </div>
  );
};
