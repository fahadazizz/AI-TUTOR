import React from 'react';

interface SystemGraphProps {
  a: number; // quad a
  b: number; // quad b
  c: number; // quad c
  m: number; // line m
  k: number; // line c (k)
}

export const SystemGraph: React.FC<SystemGraphProps> = ({ a, b, c, m, k }) => {
  const width = 300;
  const height = 300;
  const padding = 20;

  // Let's just fix the viewing window to -10 to 10 for simplicity
  const minX = -10;
  const maxX = 10;
  const minY = -10;
  const maxY = 10;

  const mapX = (x: number) => padding + ((x - minX) / (maxX - minX)) * (width - 2 * padding);
  const mapY = (y: number) => height - padding - ((y - minY) / (maxY - minY)) * (height - 2 * padding);

  // Generate parabola path
  let path1 = '';
  const points = 50;
  for (let i = 0; i <= points; i++) {
    const x = minX + (i / points) * (maxX - minX);
    const y = a * x * x + b * x + c;
    const px = mapX(x);
    const py = mapY(y);
    if (py < -50 || py > height + 50) continue; // clip
    if (path1 === '') path1 += `M ${px} ${py} `;
    else path1 += `L ${px} ${py} `;
  }

  // Generate line path
  let path2 = '';
  const yStart = m * minX + k;
  const yEnd = m * maxX + k;
  path2 = `M ${mapX(minX)} ${mapY(yStart)} L ${mapX(maxX)} ${mapY(yEnd)}`;

  const yAxisX = mapX(0);
  const xAxisY = mapY(0);

  return (
    <div style={{ margin: '1rem 0', display: 'flex', justifyContent: 'center', width: '100%' }}>
      <div style={{ backgroundColor: '#1e293b', borderRadius: '0.75rem', padding: '1rem', border: '1px solid #334155', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)' }}>
        <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} style={{ maxWidth: '100%', height: 'auto' }}>
          {/* Grid */}
          <g stroke="#334155" strokeWidth="1" strokeDasharray="4 4" opacity="0.5">
            {Array.from({ length: 21 }).map((_, i) => {
              const val = minX + i;
              if (val % 5 !== 0) return null;
              const x = mapX(val);
              return <line key={`gx-${i}`} x1={x} y1={0} x2={x} y2={height} />;
            })}
            {Array.from({ length: 21 }).map((_, i) => {
              const val = minY + i;
              if (val % 5 !== 0) return null;
              const y = mapY(val);
              return <line key={`gy-${i}`} x1={0} y1={y} x2={width} y2={y} />;
            })}
          </g>
          
          {/* Axes */}
          <line x1={Math.max(padding, Math.min(width - padding, yAxisX))} y1={padding} x2={Math.max(padding, Math.min(width - padding, yAxisX))} y2={height - padding} stroke="#64748b" strokeWidth="2" />
          <line x1={padding} y1={Math.max(padding, Math.min(height - padding, xAxisY))} x2={width - padding} y2={Math.max(padding, Math.min(height - padding, xAxisY))} stroke="#64748b" strokeWidth="2" />
          
          {/* Parabola */}
          <path d={path1} fill="none" stroke="#10b981" strokeWidth="3" style={{ filter: 'drop-shadow(0px 0px 4px rgba(16,185,129,0.5))' }} />
          
          {/* Line */}
          <path d={path2} fill="none" stroke="#f43f5e" strokeWidth="3" style={{ filter: 'drop-shadow(0px 0px 4px rgba(244,63,94,0.5))' }} />
        </svg>
      </div>
    </div>
  );
};
