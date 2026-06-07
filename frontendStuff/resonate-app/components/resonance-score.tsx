import { MODALITY_COLORS } from '@/lib/types';

interface ResonanceScoreProps {
  /** 0..1 normalized resonance */
  value: number;
  size?: number;
}

function band(score: number): { label: string; color: string } {
  if (score >= 66) return { label: 'Strong', color: MODALITY_COLORS.strong };
  if (score >= 40) return { label: 'Moderate', color: MODALITY_COLORS.overall };
  return { label: 'Weak', color: MODALITY_COLORS.dip };
}

export function ResonanceScore({ value, size = 180 }: ResonanceScoreProps) {
  const clamped = Math.max(0, Math.min(1, value));
  const score = Math.round(clamped * 100);
  const { label, color } = band(score);

  const r = 80;
  const circ = 2 * Math.PI * r;
  const arcSpan = 0.75; // 270deg gauge
  const trackLen = circ * arcSpan;
  const valueLen = trackLen * clamped;

  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
      data-testid="gauge-resonance"
    >
      <svg viewBox="0 0 200 200" width={size} height={size} className="-rotate-[135deg]">
        <defs>
          <linearGradient id="resonanceArc" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={MODALITY_COLORS.dip} />
            <stop offset="55%" stopColor={MODALITY_COLORS.overall} />
            <stop offset="100%" stopColor={MODALITY_COLORS.strong} />
          </linearGradient>
          <filter id="resonanceGlow" x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <circle
          cx="100"
          cy="100"
          r={r}
          fill="none"
          stroke="rgba(168,112,60,0.18)"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${trackLen} ${circ}`}
        />
        <circle
          cx="100"
          cy="100"
          r={r}
          fill="none"
          stroke="url(#resonanceArc)"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${valueLen} ${circ}`}
          filter="url(#resonanceGlow)"
          style={{ transition: 'stroke-dasharray 0.8s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="readout text-5xl text-white leading-none" data-testid="text-resonance-score">
          {score}
        </span>
        <span className="label-mono text-[0.5rem] text-muted-foreground mt-1">Resonance</span>
        <span className="label-mono text-[0.6rem] mt-2" style={{ color }}>
          {label}
        </span>
      </div>
    </div>
  );
}
