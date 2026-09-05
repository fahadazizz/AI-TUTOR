import React from 'react';

interface ParabolaGraphProps {
  a: number;
  b: number;
  c: number;
}

export const ParabolaGraph: React.FC<ParabolaGraphProps> = ({ a, b, c }) => {
  const width = 300;
  const height = 300;
  const padding = 20;

  // Calculate vertex
  const vx = -b / (2 * a);
  const vy = a * vx * vx + b * vx + c;

  // Determine viewing window around vertex
  const spanX = 5;
  const spanY = Math.max(10, Math.abs(vy) * 2);
  const minX = vx - spanX;
  const maxX = vx + spanX;
  const minY = Math.min(-spanY, vy - 2);
  const maxY = Math.max(spanY, vy + 2);

  const mapX = (x: number) => padding + ((x - minX) / (maxX - minX)) * (width - 2 * padding);
  const mapY = (y: number) => height - padding - ((y - minY) / (maxY - minY)) * (height - 2 * padding);

  // Generate path
  let path = '';
  const points = 50;
  for (let i = 0; i <= points; i++) {
    const x = minX + (i / points) * (maxX - minX);
    const y = a * x * x + b * x + c;
    const px = mapX(x);
    const py = mapY(y);
    if (i === 0) path += `M ${px} ${py} `;
    else path += `L ${px} ${py} `;
  }

  const yAxisX = mapX(0);
  const xAxisY = mapY(0);

  return (
    <div style={{ margin: '1rem 0', display: 'flex', justifyContent: 'center', width: '100%' }}>
      <div style={{ backgroundColor: '#1e293b', borderRadius: '0.75rem', padding: '1rem', border: '1px solid #334155', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ maxWidth: '100%', height: 'auto' }}>
          {/* Grid */}
          <g stroke="#334155" strokeWidth="1" strokeDasharray="4 4" opacity="0.5">
            {Array.from({ length: 11 }).map((_, i) => {
              const x = mapX(minX + (i / 10) * (maxX - minX));
              return <line key={`gx-${i}`} x1={x} y1={0} x2={x} y2={height} />;
            })}
            {Array.from({ length: 11 }).map((_, i) => {
              const y = mapY(minY + (i / 10) * (maxY - minY));
              return <line key={`gy-${i}`} x1={0} y1={y} x2={width} y2={y} />;
            })}
          </g>
          
          {/* Axes */}
          <line x1={Math.max(padding, Math.min(width - padding, yAxisX))} y1={padding} x2={Math.max(padding, Math.min(width - padding, yAxisX))} y2={height - padding} stroke="#64748b" strokeWidth="2" />
          <line x1={padding} y1={Math.max(padding, Math.min(height - padding, xAxisY))} x2={width - padding} y2={Math.max(padding, Math.min(height - padding, xAxisY))} stroke="#64748b" strokeWidth="2" />
          
          {/* Parabola */}
          <path d={path} fill="none" stroke="#10b981" strokeWidth="3" style={{ filter: 'drop-shadow(0px 0px 4px rgba(16,185,129,0.5))' }} />
          
          {/* Vertex Dot */}
          <circle cx={mapX(vx)} cy={mapY(vy)} r="4" fill="#3b82f6" />
          <text x={mapX(vx) + 8} y={mapY(vy) - 8} fill="#94a3b8" fontSize="12" fontFamily="sans-serif">
            ({vx.toFixed(1)}, {vy.toFixed(1)})
          </text>
        </svg>
      </div>
    </div>
  );
};
