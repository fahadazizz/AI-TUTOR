import React from 'react';

interface RootsNatureProps {
  discriminant: number;
}

export const RootsNature: React.FC<RootsNatureProps> = ({ discriminant }) => {
  const isPos = discriminant > 0;
  const isZero = discriminant === 0;
  const isNeg = discriminant < 0;

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
        gap: '1.5rem',
        width: '100%',
        maxWidth: '500px'
      }}>
        
        <div style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#334155',
          borderRadius: '0.5rem',
          border: '2px solid #475569',
          color: '#f8fafc',
          fontWeight: 'bold',
          textAlign: 'center'
        }}>
          Discriminant (Δ) = {discriminant}
        </div>

        {/* Down Arrow */}
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <polyline points="19 12 12 19 5 12"></polyline>
        </svg>

        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', gap: '1rem' }}>
          
          <div style={{
            flex: 1,
            padding: '1rem',
            backgroundColor: isPos ? '#064e3b' : '#1e293b',
            borderRadius: '0.5rem',
            border: `2px solid ${isPos ? '#10b981' : '#334155'}`,
            opacity: isPos ? 1 : 0.4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ color: isPos ? '#10b981' : '#94a3b8', fontWeight: 'bold' }}>Δ &gt; 0</div>
            <div style={{ color: '#f8fafc', fontSize: '0.875rem', textAlign: 'center' }}>Two Real<br/>Distinct Roots</div>
          </div>

          <div style={{
            flex: 1,
            padding: '1rem',
            backgroundColor: isZero ? '#1e3a8a' : '#1e293b',
            borderRadius: '0.5rem',
            border: `2px solid ${isZero ? '#3b82f6' : '#334155'}`,
            opacity: isZero ? 1 : 0.4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ color: isZero ? '#3b82f6' : '#94a3b8', fontWeight: 'bold' }}>Δ = 0</div>
            <div style={{ color: '#f8fafc', fontSize: '0.875rem', textAlign: 'center' }}>Two Real<br/>Equal Roots</div>
          </div>

          <div style={{
            flex: 1,
            padding: '1rem',
            backgroundColor: isNeg ? '#7f1d1d' : '#1e293b',
            borderRadius: '0.5rem',
            border: `2px solid ${isNeg ? '#ef4444' : '#334155'}`,
            opacity: isNeg ? 1 : 0.4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '0.5rem',
            transition: 'all 0.3s ease'
          }}>
            <div style={{ color: isNeg ? '#ef4444' : '#94a3b8', fontWeight: 'bold' }}>Δ &lt; 0</div>
            <div style={{ color: '#f8fafc', fontSize: '0.875rem', textAlign: 'center' }}>Imaginary<br/>Complex Roots</div>
          </div>

        </div>
      </div>
    </div>
  );
};
