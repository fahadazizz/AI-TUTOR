import React from 'react';

interface NumberLineProps {
  interval: string; // e.g. "[2,5]", "(-inf, 3]", "[4, inf)"
}

export const NumberLine: React.FC<NumberLineProps> = ({ interval }) => {
  const width = 400;
  const height = 100;
  const padding = 30;

  // Extremely basic interval parsing
  let min = -10;
  let max = 10;
  let startVal = -5;
  let endVal = 5;
  let startInclusive = true;
  let endInclusive = true;
  let toInf = false;
  let toNegInf = false;

  const match = interval.match(/^([\[\(])\s*(.*?)\s*,\s*(.*?)\s*([\]\)])$/);
  if (match) {
    startInclusive = match[1] === '[';
    endInclusive = match[4] === ']';
    
    if (match[2].includes('inf')) {
      toNegInf = true;
      startVal = min;
    } else {
      startVal = parseFloat(match[2]);
    }
    
    if (match[3].includes('inf')) {
      toInf = true;
      endVal = max;
    } else {
      endVal = parseFloat(match[3]);
    }

    // Auto-scale if needed
    if (!toNegInf && !toInf) {
      const center = (startVal + endVal) / 2;
      const span = Math.max(endVal - startVal + 4, 10);
      min = center - span / 2;
      max = center + span / 2;
    } else if (toNegInf && !toInf) {
      max = endVal + 5;
      min = endVal - 15;
      startVal = min;
    } else if (!toNegInf && toInf) {
      min = startVal - 5;
      max = startVal + 15;
      endVal = max;
    }
  }

  const mapX = (x: number) => padding + ((x - min) / (max - min)) * (width - 2 * padding);
  const cy = height / 2;

  const startX = mapX(startVal);
  const endX = mapX(endVal);

  return (
    <div style={{ margin: '1rem 0', display: 'flex', justifyContent: 'center', width: '100%' }}>
      <div style={{ backgroundColor: '#1e293b', borderRadius: '0.75rem', padding: '1rem', border: '1px solid #334155', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ maxWidth: '100%', height: 'auto' }}>
          {/* Main Axis */}
          <line x1={padding} y1={cy} x2={width - padding} y2={cy} stroke="#64748b" strokeWidth="2" />
          
          {/* Ticks */}
          {Array.from({ length: Math.floor(max - min) + 1 }).map((_, i) => {
            const val = Math.ceil(min) + i;
            if (val > max) return null;
            const x = mapX(val);
            return (
              <g key={`tick-${val}`}>
                <line x1={x} y1={cy - 5} x2={x} y2={cy + 5} stroke="#64748b" strokeWidth="1" />
                <text x={x} y={cy + 20} fill="#94a3b8" fontSize="10" textAnchor="middle" fontFamily="sans-serif">
                  {val}
                </text>
              </g>
            );
          })}

          {/* Highlighted Interval Line */}
          <line 
            x1={startX} 
            y1={cy} 
            x2={endX} 
            y2={cy} 
            stroke="#10b981" 
            strokeWidth="4" 
            style={{ filter: 'drop-shadow(0px 0px 4px rgba(16,185,129,0.5))' }}
          />

          {/* Endpoints */}
          {!toNegInf && (
            <circle 
              cx={startX} 
              cy={cy} 
              r="5" 
              fill={startInclusive ? "#10b981" : "#1e293b"} 
              stroke="#10b981" 
              strokeWidth="2" 
            />
          )}
          {!toInf && (
            <circle 
              cx={endX} 
              cy={cy} 
              r="5" 
              fill={endInclusive ? "#10b981" : "#1e293b"} 
              stroke="#10b981" 
              strokeWidth="2" 
            />
          )}

          {/* Infinity Arrows */}
          {toInf && (
            <path d={`M ${width - padding - 8} ${cy - 5} L ${width - padding + 2} ${cy} L ${width - padding - 8} ${cy + 5}`} fill="#10b981" />
          )}
          {toNegInf && (
            <path d={`M ${padding + 8} ${cy - 5} L ${padding - 2} ${cy} L ${padding + 8} ${cy + 5}`} fill="#10b981" />
          )}
        </svg>
      </div>
    </div>
  );
};
