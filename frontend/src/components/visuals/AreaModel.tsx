import React from 'react';

interface AreaModelProps {
  a: number;
  b: number;
  c: number;
  split1: number;
  split2: number;
}

export const AreaModel: React.FC<AreaModelProps> = ({ a, b, c, split1, split2 }) => {
  const ax2 = a === 1 ? 'x²' : `${a}x²`;
  const s1 = split1 === 1 ? 'x' : split1 === -1 ? '-x' : `${split1}x`;
  const s2 = split2 === 1 ? 'x' : split2 === -1 ? '-x' : `${split2}x`;
  
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
        gap: '1rem',
        width: '100%',
        maxWidth: '400px'
      }}>
        
        <div style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '0.5rem' }}>
          Area Model (Splitting the Middle Term)
        </div>
        
        <div style={{ color: '#f8fafc', fontSize: '1.2rem', fontFamily: 'serif' }}>
          {a === 1 ? '' : a}x² {b < 0 ? '-' : '+'} {Math.abs(b)}x {c < 0 ? '-' : '+'} {Math.abs(c)}
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: '1fr 1fr', 
          gridTemplateRows: '1fr 1fr',
          gap: '4px',
          backgroundColor: '#334155',
          border: '4px solid #334155',
          borderRadius: '0.5rem',
          overflow: 'hidden',
          width: '200px',
          height: '200px',
          marginTop: '1rem'
        }}>
          
          <div style={{ backgroundColor: '#1e3a8a', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f8fafc', fontSize: '1.5rem', fontFamily: 'serif' }}>
            {ax2}
          </div>
          <div style={{ backgroundColor: '#064e3b', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f8fafc', fontSize: '1.5rem', fontFamily: 'serif' }}>
            {s1}
          </div>
          <div style={{ backgroundColor: '#064e3b', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f8fafc', fontSize: '1.5rem', fontFamily: 'serif' }}>
            {s2}
          </div>
          <div style={{ backgroundColor: '#7f1d1d', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#f8fafc', fontSize: '1.5rem', fontFamily: 'serif' }}>
            {c}
          </div>

        </div>

      </div>
    </div>
  );
};
