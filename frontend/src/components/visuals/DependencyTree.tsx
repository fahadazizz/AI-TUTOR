import React from 'react';

interface DependencyTreeProps {
  concept_name: string;
  prerequisites: string; // comma separated
}

export const DependencyTree: React.FC<DependencyTreeProps> = ({ concept_name, prerequisites }) => {
  const prereqs = prerequisites.split(',').map(p => p.trim());
  
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
        maxWidth: '500px'
      }}>
        
        <div style={{ color: '#94a3b8', fontSize: '1.1rem', marginBottom: '1rem' }}>
          Concept Dependencies
        </div>

        {/* Current Concept */}
        <div style={{
          padding: '0.75rem 1.5rem',
          backgroundColor: '#3b82f6',
          borderRadius: '0.5rem',
          border: '2px solid #2563eb',
          color: '#ffffff',
          fontWeight: 'bold',
          textAlign: 'center',
          zIndex: 10
        }}>
          {concept_name}
        </div>

        {prereqs.length > 0 && prereqs[0] !== '' && (
          <>
            {/* Arrows */}
            <div style={{ display: 'flex', justifyContent: 'space-around', width: '80%', height: '40px', position: 'relative' }}>
              {prereqs.map((_, i) => (
                <svg key={`line-${i}`} style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                  <line 
                    x1="50%" y1="0" 
                    x2={`${(i + 1) * (100 / (prereqs.length + 1))}%`} y2="100%" 
                    stroke="#64748b" strokeWidth="2" 
                  />
                  <polygon 
                    points={`${(i + 1) * (100 / (prereqs.length + 1))}% 100%, ${(i + 1) * (100 / (prereqs.length + 1))}% calc(100% - 10px), calc(${(i + 1) * (100 / (prereqs.length + 1))}% - 5px) calc(100% - 10px)`} 
                    fill="#64748b" 
                    transform={`translate(0, -5)`}
                  />
                </svg>
              ))}
            </div>

            {/* Prerequisites */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap', width: '100%' }}>
              {prereqs.map((p, i) => (
                <div key={i} style={{
                  padding: '0.5rem 1rem',
                  backgroundColor: '#334155',
                  borderRadius: '0.5rem',
                  border: '2px solid #475569',
                  color: '#e2e8f0',
                  textAlign: 'center',
                  fontSize: '0.9rem'
                }}>
                  {p}
                </div>
              ))}
            </div>
          </>
        )}

      </div>
    </div>
  );
};
