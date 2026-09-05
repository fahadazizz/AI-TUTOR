import React from 'react';

interface CompletingSquareProps {
  b: number;
}

export const CompletingSquare: React.FC<CompletingSquareProps> = ({ b }) => {
  const width = 300;
  const height = 300;
  
  const b_half = b / 2;
  const b_half_str = b_half % 1 === 0 ? b_half.toString() : b_half.toFixed(1);
  const b_half_sq = b_half * b_half;
  const b_half_sq_str = b_half_sq % 1 === 0 ? b_half_sq.toString() : b_half_sq.toFixed(2);
  
  // Dimensions for visualization
  const xSize = 160;
  const rectSize = 50;

  return (
    <div style={{ margin: '1rem 0', display: 'flex', justifyContent: 'center', width: '100%' }}>
      <div style={{ backgroundColor: '#1e293b', borderRadius: '0.75rem', padding: '1.5rem', border: '1px solid #334155', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ maxWidth: '100%', height: 'auto' }}>
          
          {/* Main x^2 Square */}
          <rect x="20" y="20" width={xSize} height={xSize} fill="#3b82f6" opacity="0.8" stroke="#2563eb" strokeWidth="2" />
          <text x={20 + xSize/2} y={20 + xSize/2} fill="#ffffff" fontSize="24" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">
            x²
          </text>

          {/* Right Rectangle (b/2)x */}
          <rect x={20 + xSize} y="20" width={rectSize} height={xSize} fill="#10b981" opacity="0.8" stroke="#059669" strokeWidth="2" />
          <text x={20 + xSize + rectSize/2} y={20 + xSize/2} fill="#ffffff" fontSize="16" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif" transform={`rotate(-90 ${20 + xSize + rectSize/2} ${20 + xSize/2})`}>
            {b_half_str}x
          </text>

          {/* Bottom Rectangle (b/2)x */}
          <rect x="20" y={20 + xSize} width={xSize} height={rectSize} fill="#10b981" opacity="0.8" stroke="#059669" strokeWidth="2" />
          <text x={20 + xSize/2} y={20 + xSize + rectSize/2} fill="#ffffff" fontSize="16" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">
            {b_half_str}x
          </text>

          {/* Missing Square (b/2)^2 */}
          <rect x={20 + xSize} y={20 + xSize} width={rectSize} height={rectSize} fill="transparent" stroke="#f59e0b" strokeWidth="2" strokeDasharray="4 4" />
          <text x={20 + xSize + rectSize/2} y={20 + xSize + rectSize/2} fill="#f59e0b" fontSize="12" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">
            {b_half_sq_str}
          </text>
          
          {/* Labels for side lengths */}
          <text x={20 + xSize/2} y="12" fill="#94a3b8" fontSize="12" textAnchor="middle" fontFamily="sans-serif">x</text>
          <text x={20 + xSize + rectSize/2} y="12" fill="#94a3b8" fontSize="12" textAnchor="middle" fontFamily="sans-serif">{b_half_str}</text>
          
          <text x="8" y={20 + xSize/2} fill="#94a3b8" fontSize="12" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">x</text>
          <text x="8" y={20 + xSize + rectSize/2} fill="#94a3b8" fontSize="12" textAnchor="middle" dominantBaseline="middle" fontFamily="sans-serif">{b_half_str}</text>

        </svg>
      </div>
    </div>
  );
};
