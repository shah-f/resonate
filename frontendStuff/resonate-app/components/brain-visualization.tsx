import { useRef, useMemo, useState, Component, type ReactNode } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Instances, Instance, Html } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import { ResonateResult, MODALITY_COLORS, type Modality } from '@/lib/types';

interface BrainVisualizationProps {
  result: ResonateResult;
  currentTime: number;
}

type ViewMode = 'modality' | 'parcels';

const PARCEL_COUNT = 200;
const BRAIN_RADIUS = 5;
const MODALITIES: Modality[] = ['visual', 'audio', 'language'];

// Approximate anchor positions for each modality "region" blob (visually distributed,
// not exact anatomy — matches the disclaimer caption).
const MODALITY_ANCHORS: Record<Modality, [number, number, number]> = {
  visual: [-3.4, -3.0, 2.8],
  audio: [4.8, -0.8, -2.8],
  language: [-3.6, 3.0, 1.0],
};

function getTimeIndex(segments: ResonateResult['brain']['segments'], currentTime: number): number {
  for (let i = 0; i < segments.length; i++) {
    if (currentTime >= segments[i].start && currentTime <= segments[i].end) return i;
  }
  if (segments.length && currentTime >= segments[segments.length - 1].end) return segments.length - 1;
  return 0;
}

// Generate deterministic points in a brain-like shape (two hemispheres)
function generateBrainPoints(): THREE.Vector3[] {
  const points: THREE.Vector3[] = [];
  // seeded random for consistent layout
  const random = () => {
    let seed = 1;
    return () => {
      const x = Math.sin(seed++) * 10000;
      return x - Math.floor(x);
    };
  };
  const rand = random();

  for (let i = 0; i < PARCEL_COUNT; i++) {
    const isLeft = i < PARCEL_COUNT / 2;
    // Ellipsoid distribution
    const u = rand() * Math.PI * 2;
    const v = rand() * Math.PI;

    // Scale X more to make it longer front-to-back, scale Z for width, Y for height
    const x = Math.sin(v) * Math.cos(u) * BRAIN_RADIUS * 1.2;
    const y = Math.sin(v) * Math.sin(u) * BRAIN_RADIUS * 0.8;
    const z = Math.cos(v) * BRAIN_RADIUS * 0.7;

    // Separate hemispheres
    const zOffset = isLeft ? -0.8 : 0.8;

    points.push(new THREE.Vector3(x, y, z + zOffset));
  }
  return points;
}

const brainPoints = generateBrainPoints();

// Organic brain-like outline: a sphere deformed with layered sine "gyri" bumps,
// scaled into a brain-proportioned ellipsoid that encloses the parcel nodes.
function BrainShell() {
  const geometry = useMemo(() => {
    const geo = new THREE.SphereGeometry(1, 96, 64);
    const pos = geo.attributes.position as THREE.BufferAttribute;
    const v = new THREE.Vector3();
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      // Layered sine folds approximate cortical gyri.
      const folds =
        0.05 * Math.sin(v.x * 7.0) * Math.sin(v.y * 7.0) * Math.sin(v.z * 7.0) +
        0.035 * Math.sin(v.x * 13.0 + v.y * 5.0) +
        0.03 * Math.sin(v.z * 11.0 + v.x * 4.0);
      // Longitudinal fissure: pinch the surface near the midline (z ≈ 0).
      const fissure = -0.12 * Math.exp(-(v.z * v.z) / 0.02);
      v.multiplyScalar(1 + folds + fissure);
      pos.setXYZ(i, v.x, v.y, v.z);
    }
    pos.needsUpdate = true;
    geo.computeVertexNormals();
    return geo;
  }, []);

  return (
    <group scale={[BRAIN_RADIUS * 1.32, BRAIN_RADIUS * 0.92, BRAIN_RADIUS * 0.94]}>
      {/* Soft inner volume for depth/occlusion */}
      <mesh geometry={geometry} scale={0.985}>
        <meshBasicMaterial color="#050510" transparent opacity={0.35} side={THREE.BackSide} />
      </mesh>
      {/* Wireframe outline */}
      <mesh geometry={geometry}>
        <meshBasicMaterial color="#3b82f6" wireframe transparent opacity={0.12} toneMapped={false} />
      </mesh>
    </group>
  );
}

function ParcelNodes({ result, currentTime }: BrainVisualizationProps) {
  const timeIndex = useMemo(
    () => getTimeIndex(result.brain.segments, currentTime),
    [currentTime, result.brain.segments]
  );
  const [hoveredNode, setHoveredNode] = useState<number | null>(null);

  const getModalityColor = (index: number) => {
    if (result.brain.modalityIndices?.visual.includes(index)) return MODALITY_COLORS.visual;
    if (result.brain.modalityIndices?.audio.includes(index)) return MODALITY_COLORS.audio;
    if (result.brain.modalityIndices?.language.includes(index)) return MODALITY_COLORS.language;
    return MODALITY_COLORS.overall;
  };

  const getModalityName = (index: number) => {
    if (result.brain.modalityIndices?.visual.includes(index)) return 'Visual';
    if (result.brain.modalityIndices?.audio.includes(index)) return 'Audio';
    if (result.brain.modalityIndices?.language.includes(index)) return 'Language';
    return 'Mixed';
  };

  return (
    <Instances range={PARCEL_COUNT} limit={PARCEL_COUNT}>
      <sphereGeometry args={[0.2, 16, 16]} />
      <meshBasicMaterial toneMapped={false} />
      {brainPoints.map((pos, i) => {
        const val = result.brain.parcels ? result.brain.parcels[i]?.[timeIndex] ?? 0.1 : 0.1;
        const color = new THREE.Color(getModalityColor(i));
        const intensity = 0.5 + val * 2;
        color.multiplyScalar(intensity);

        const scale = 0.5 + val * 1.5;
        const isHovered = hoveredNode === i;

        return (
          <group key={i} position={pos}>
            <Instance
              scale={isHovered ? scale * 1.5 : scale}
              color={color}
              onPointerOver={(e) => { e.stopPropagation(); setHoveredNode(i); }}
              onPointerOut={(e) => { e.stopPropagation(); setHoveredNode(null); }}
            />
            {isHovered && (
              <Html distanceFactor={15} center>
                <div className="bg-popover/90 backdrop-blur border border-popover-border p-2 rounded text-xs whitespace-nowrap pointer-events-none" data-testid={`tooltip-brain-node-${i}`}>
                  <p className="font-medium text-white">{result.brain.parcelNames?.[i] ?? `Parcel ${i}`}</p>
                  <p className="text-muted-foreground">Modality: {getModalityName(i)}</p>
                  <p className="text-primary mt-1">Value: {(val * 100).toFixed(1)}%</p>
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </Instances>
  );
}

function ModalityBlobs({ result, currentTime, selected }: BrainVisualizationProps & { selected: Modality }) {
  const timeIndex = useMemo(
    () => getTimeIndex(result.brain.segments, currentTime),
    [currentTime, result.brain.segments]
  );

  return (
    <group>
      {MODALITIES.map((mod) => {
        const val = result.brain.modality[mod]?.[timeIndex] ?? 0;
        const isSelected = selected === mod;
        const color = new THREE.Color(MODALITY_COLORS[mod]);
        color.multiplyScalar(isSelected ? 1.2 + val * 2.0 : 0.4 + val * 0.6);
        // Compact glow that stays smaller than the brain shell and well separated.
        const size = BRAIN_RADIUS * (0.18 + val * 0.2) * (isSelected ? 1.3 : 0.7);

        return (
          <mesh key={mod} position={MODALITY_ANCHORS[mod]}>
            <sphereGeometry args={[size, 32, 32]} />
            <meshBasicMaterial
              color={color}
              transparent
              opacity={isSelected ? 0.6 : 0.18}
              blending={THREE.AdditiveBlending}
              depthWrite={false}
              toneMapped={false}
            />
          </mesh>
        );
      })}
    </group>
  );
}

function BrainScene({
  result,
  currentTime,
  viewMode,
  selectedModality,
}: BrainVisualizationProps & { viewMode: ViewMode; selectedModality: Modality }) {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.2;
      groupRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.05) * 0.1;
    }
  });

  return (
    <group ref={groupRef}>
      <BrainShell />
      {viewMode === 'parcels' ? (
        <ParcelNodes result={result} currentTime={currentTime} />
      ) : (
        <ModalityBlobs result={result} currentTime={currentTime} selected={selectedModality} />
      )}
    </group>
  );
}

function ModalityBars({ result, currentTime, selected }: BrainVisualizationProps & { selected?: Modality }) {
  const timeIndex = getTimeIndex(result.brain.segments, currentTime);
  return (
    <div className="w-full h-full min-h-[300px] flex items-center justify-center bg-[#0a0a0f] overflow-hidden">
      <div className="text-center space-y-4">
        <div className="flex gap-8 justify-center">
          {MODALITIES.map((mod) => {
            const val = (result.brain.modality[mod][timeIndex] ?? 0) * 100;
            const isSelected = selected === mod;
            return (
              <div key={mod} className="flex flex-col items-center gap-2">
                <div className={`w-16 h-32 bg-muted/30 rounded-full relative overflow-hidden flex items-end transition-all ${isSelected ? 'ring-2 ring-primary/60' : ''}`}>
                  <div
                    className="w-full rounded-full transition-all duration-300"
                    style={{
                      height: `${val}%`,
                      backgroundColor: MODALITY_COLORS[mod],
                      boxShadow: `0 0 20px ${MODALITY_COLORS[mod]}`,
                      opacity: isSelected || !selected ? 1 : 0.4,
                    }}
                  />
                </div>
                <span className="label-mono text-[0.7rem] text-muted-foreground">{mod}</span>
                <span className="readout text-sm text-white">{val.toFixed(0)}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// Detect WebGL support once at module load so we can avoid mounting the Canvas
// (which throws an uncatchable error overlay in dev) on machines without WebGL.
function detectWebGL(): boolean {
  if (typeof document === 'undefined') return false;
  try {
    const canvas = document.createElement('canvas');
    return !!(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch {
    return false;
  }
}

const WEBGL_SUPPORTED = detectWebGL();

// Catches any runtime error from the three.js render tree and falls back to bars.
class BrainErrorBoundary extends Component<
  { fallback: ReactNode; children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    return this.state.hasError ? this.props.fallback : this.props.children;
  }
}

export function BrainVisualization({ result, currentTime }: BrainVisualizationProps) {
  const [viewMode, setViewMode] = useState<ViewMode>('modality');
  const [selectedModality, setSelectedModality] = useState<Modality>('visual');

  const hasParcels = !!result.brain.parcels && result.brain.parcels.length > 0;
  const canRender3D = hasParcels && WEBGL_SUPPORTED;
  const showTabs = viewMode === 'modality' || !canRender3D;

  return (
    <div
      className="w-full h-full min-h-[480px] bg-[#0a0a0f] rounded-lg border border-card-border overflow-hidden relative"
      data-testid="panel-brain-viz"
    >
      {/* Header */}
      <div className="absolute top-4 left-4 z-10 pointer-events-none">
        <h3 className="label-mono text-[0.7rem] text-primary text-glow">Brain Activation</h3>
      </div>

      {/* View toggle */}
      {canRender3D && (
        <div className="absolute top-3 right-3 z-10 flex items-center gap-1 rounded-full border border-white/10 bg-black/40 p-1 backdrop-blur">
          {([['modality', 'Modality'], ['parcels', '200 Parcels']] as const).map(([mode, label]) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              data-testid={`button-view-${mode}`}
              className={`label-mono px-4 py-1.5 text-[0.62rem] rounded-full transition-colors ${
                viewMode === mode ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-white'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      )}

      {/* Visualization */}
      <div className="absolute inset-0">
        {canRender3D ? (
          <BrainErrorBoundary
            fallback={<ModalityBars result={result} currentTime={currentTime} selected={selectedModality} />}
          >
            <Canvas camera={{ position: [0, 0, 12], fov: 45 }} className="cursor-move">
              <color attach="background" args={['#0a0a0f']} />
              <ambientLight intensity={0.2} />
              <BrainScene
                result={result}
                currentTime={currentTime}
                viewMode={viewMode}
                selectedModality={selectedModality}
              />
              <OrbitControls enablePan={false} maxDistance={20} minDistance={5} />
              <EffectComposer>
                <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.9} height={300} intensity={1.5} />
              </EffectComposer>
            </Canvas>
          </BrainErrorBoundary>
        ) : (
          <ModalityBars result={result} currentTime={currentTime} selected={selectedModality} />
        )}
      </div>

      {/* Bottom chrome: modality tabs + caption stacked so they never overlap */}
      <div className="absolute bottom-0 left-0 right-0 z-10 flex flex-col items-center gap-3 px-4 pb-3 pt-8 bg-gradient-to-t from-[#0a0a0f] via-[#0a0a0f]/85 to-transparent pointer-events-none">
        {showTabs && (
          <div className="flex flex-wrap justify-center gap-2 pointer-events-auto">
            {MODALITIES.map((mod) => {
              const isSelected = selectedModality === mod;
              return (
                <button
                  key={mod}
                  onClick={() => setSelectedModality(mod)}
                  data-testid={`button-modality-${mod}`}
                  className={`label-mono flex items-center gap-2 rounded-full px-4 py-1.5 text-[0.62rem] transition-all border ${
                    isSelected
                      ? 'bg-primary text-primary-foreground border-transparent shadow-[0_0_16px_rgba(249,115,22,0.5)]'
                      : 'border-white/10 bg-black/40 text-muted-foreground hover:text-white'
                  }`}
                >
                  {!isSelected && (
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: MODALITY_COLORS[mod] }} />
                  )}
                  {mod}
                </button>
              );
            })}
          </div>
        )}
        <p className="text-center font-mono text-[10px] leading-tight tracking-wide text-muted-foreground/80">
          Schaefer-200 parcel visualization — approximate hemispheric layout, not exact anatomical coordinates.
        </p>
      </div>
    </div>
  );
}
