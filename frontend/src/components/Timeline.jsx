import React from 'react'

export default function Timeline({ series = [], duration = 1, currentTime = 0, dips = [], onSeek }) {
  const width = 800
  const height = 80

  const points = series.map((v, i) => {
    const x = (i / Math.max(1, series.length - 1)) * (width - 20) + 10
    const y = height - (v * (height - 20) + 10)
    return [x, y]
  })

  const pathD = points.map((p, i) => (i === 0 ? `M ${p[0]} ${p[1]}` : `L ${p[0]} ${p[1]}`)).join(' ')

  const playheadX = (currentTime / Math.max(0.0001, duration)) * (width - 20) + 10

  return (
    <div className="timeline-root">
      <svg viewBox={`0 0 ${width} ${height}`} className="timeline-svg">
        <defs>
          <linearGradient id="g" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#7dd3fc" stopOpacity="0.16" />
            <stop offset="100%" stopColor="#0ea5a0" stopOpacity="0.02" />
          </linearGradient>
        </defs>
        <path d={pathD} fill="none" stroke="#60a5fa" strokeWidth="2" />
        <path d={`${pathD} L ${width-10} ${height} L 10 ${height} Z`} fill="url(#g)" opacity="0.6" />

        {dips.map((d, i) => {
          const x = (d.time / Math.max(0.0001, duration)) * (width - 20) + 10
          return (
            <g key={i} onClick={() => onSeek && onSeek(d.time)} style={{ cursor: 'pointer' }}>
              <circle cx={x} cy={height - 12} r={6} fill="#ef4444" />
              <text x={x} y={height - 22} textAnchor="middle" fontSize="10" fill="#ffefef">{d.label || 'dip'}</text>
            </g>
          )
        })}

        <line x1={playheadX} x2={playheadX} y1={6} y2={height - 6} stroke="#ffffff" strokeWidth="1" opacity="0.9" />
      </svg>
      <div className="timeline-controls">Click a marker to jump to that moment</div>
    </div>
  )
}
