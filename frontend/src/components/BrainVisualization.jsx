import React, { useMemo, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Html } from '@react-three/drei'

function hemisphereLayout(count) {
  const positions = []
  const half = Math.ceil(count / 2)
  for (let i = 0; i < count; i++) {
    const isLeft = i < half
    const idx = isLeft ? i : i - half
    const n = half
    const theta = idx * (Math.PI * 2 / Math.max(1, n))
    const r = 1.2 * (0.25 + 0.75 * (idx / Math.max(1, n)))
    const x = (isLeft ? -1 : 1) * (0.6 + Math.cos(theta) * r)
    const y = Math.sin(theta) * r * 0.6
    const z = (Math.sin(idx * 0.3) * 0.2)
    positions.push([x, y, z])
  }
  return positions
}

function Parcel({ pos, color, value, scale = 1, onHover, onOut, onClick, hovered }) {
  return (
    <mesh position={pos} scale={[scale, scale, scale]} onPointerOver={onHover} onPointerOut={onOut} onClick={onClick}>
      <sphereGeometry args={[0.06, 12, 12]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={value * 1.6} transparent opacity={0.85} />
      {hovered && (
        <Html distanceFactor={8} center style={{ pointerEvents: 'none' }}>
          <div className="parcel-tooltip" style={{ transform: 'translateY(-50%)' }}>
            <div className="parcel-name">{hovered.name}</div>
            <div className="parcel-value">{hovered.value}%</div>
          </div>
        </Html>
      )}
    </mesh>
  )
}

export default function BrainVisualization({ currentTime = 0, duration = 15, parcels = [], parcelNames = [], modalityIndices = {}, parcelPositions = null }) {
  const count = (parcelPositions && parcelPositions.length) || (parcels && parcels[0] && parcels[0].length) || 200
  const positions = useMemo(() => parcelPositions ? parcelPositions : hemisphereLayout(count), [count, parcelPositions])
  const tIndex = Math.max(0, Math.min((parcels.length || 1) - 1, Math.round((currentTime / Math.max(0.0001, duration)) * Math.max(1, (parcels.length || 1) - 1))))
  const values = parcels && parcels.length ? parcels[tIndex] : Array.from({ length: count }, () => 0.3)

  const [hovered, setHovered] = useState(null)

  const getColor = (i) => {
    if (modalityIndices.visual && modalityIndices.visual.includes(i)) return '#3b82f6'
    if (modalityIndices.audio && modalityIndices.audio.includes(i)) return '#22c55e'
    if (modalityIndices.language && modalityIndices.language.includes(i)) return '#f43f5e'
    return '#98a2b3'
  }

  return (
    <div style={{ width: '100%', height: 360 }}>
      <Canvas camera={{ position: [0, 0, 4.8], fov: 45 }} dpr={[1, 2]}>
        <ambientLight intensity={0.35} />
        <pointLight position={[4, 5, 4]} intensity={1.0} color={'#9ec5ff'} />
        <pointLight position={[-4, -2, -3]} intensity={0.6} color={'#c4a3ff'} />

        <group rotation={[0.15, 0, 0]}>
          {/* translucent shell */}
          <mesh scale={[1.85, 1.35, 1.55]}> 
            <sphereGeometry args={[1, 48, 48]} />
            <meshStandardMaterial color={'#07102a'} transparent opacity={0.06} wireframe={false} />
          </mesh>

          {/* parcel cloud */}
          {positions.map((p, i) => {
            const val = values[i] ?? 0.3
            const name = parcelNames[i] || `Parcel ${i + 1}`
            const color = getColor(i)
            const top = i < 10 // simple emphasis heuristic
            return (
              <Parcel
                key={i}
                pos={p}
                color={color}
                value={val}
                scale={0.8 + val * 1.6}
                hovered={hovered && hovered.index === i ? { name, value: Math.round(val * 100) } : null}
                onHover={(e) => {
                  e.stopPropagation()
                  setHovered({ index: i })
                }}
                onOut={(e) => { e.stopPropagation(); setHovered(null) }}
                onClick={() => { /* noop for now */ }}
              />
            )
          })}

        </group>

        <OrbitControls enableZoom enablePan={false} autoRotate={false} />
      </Canvas>
      <div className="legend" style={{ position: 'absolute', right: 12, bottom: 12 }}>
        <div><span className="dot visual"/> Visual</div>
        <div><span className="dot audio"/> Audio</div>
        <div><span className="dot language"/> Language</div>
      </div>
    </div>
  )
}
