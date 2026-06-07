import { ResonateResult, MODALITY_COLORS } from '@/lib/types';
import { ResonanceScore } from '@/components/resonance-score';
import { ArrowUpRight, TrendingDown, Activity, AlertTriangle } from 'lucide-react';

interface MissionHeaderProps {
  result: ResonateResult;
  onSeek: (time: number) => void;
}

interface StatTileProps {
  label: string;
  value: string;
  accent: string;
  icon: React.ReactNode;
  onClick?: () => void;
  testId?: string;
}

function StatTile({ label, value, accent, icon, onClick, testId }: StatTileProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={!onClick}
      data-testid={testId}
      className="group flex flex-col gap-2 p-4 text-left bg-black/30 border border-card-border hover:border-primary/40 transition-colors disabled:cursor-default disabled:hover:border-card-border"
    >
      <div className="flex items-center justify-between">
        <span className="label-mono text-[0.52rem] text-muted-foreground">{label}</span>
        <span style={{ color: accent }}>{icon}</span>
      </div>
      <span className="readout text-xl text-white leading-none">{value}</span>
    </button>
  );
}

export function MissionHeader({ result, onSeek }: MissionHeaderProps) {
  const { insights, brain, filename, duration } = result;

  const strongest = insights.rankedMoments.strongest[0];
  const weakest = insights.rankedMoments.weakest[0];
  const dominant = insights.modalityBalance.dominant;

  const overall = brain.overall;
  const meanResonance =
    overall.length > 0 ? overall.reduce((a, b) => a + b, 0) / overall.length : 0;

  return (
    <section
      className="relative overflow-hidden bg-card/40 border border-card-border glow-primary"
      data-testid="panel-mission-header"
    >
      <div
        className="pointer-events-none absolute -top-24 -right-16 w-80 h-80 rounded-full opacity-40 blur-3xl"
        style={{ background: 'radial-gradient(circle, rgba(249,115,22,0.35), transparent 70%)' }}
      />
      <div className="relative grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-8 p-5 sm:p-7">
        <div className="flex flex-col">
          <div className="flex items-center gap-3 mb-4">
            <span className="label-mono text-[0.6rem] text-primary">Diagnosis</span>
            {filename && (
              <span className="label-mono text-[0.56rem] text-muted-foreground truncate">
                {filename} · {duration.toFixed(0)}s
              </span>
            )}
          </div>

          <h2 className="text-2xl sm:text-3xl font-semibold text-white leading-tight max-w-2xl mb-6">
            The payoff lands late: the strongest predicted response is at{' '}
            <span className="text-primary">
              {strongest.start.toFixed(1)}–{strongest.end.toFixed(1)}s
            </span>
            , while the hook stays flat.
          </h2>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-card-border mt-auto">
            <StatTile
              label="Strongest"
              value={`${strongest.start.toFixed(1)}s`}
              accent={MODALITY_COLORS.strong}
              icon={<ArrowUpRight className="w-4 h-4" />}
              onClick={() => onSeek(strongest.start)}
              testId="stat-strongest"
            />
            <StatTile
              label="Weakest"
              value={`${weakest.start.toFixed(1)}s`}
              accent={MODALITY_COLORS.dip}
              icon={<TrendingDown className="w-4 h-4" />}
              onClick={() => onSeek(weakest.start)}
              testId="stat-weakest"
            />
            <StatTile
              label="Dominant Signal"
              value={dominant.charAt(0).toUpperCase() + dominant.slice(1)}
              accent={MODALITY_COLORS[dominant]}
              icon={<Activity className="w-4 h-4" />}
              testId="stat-dominant"
            />
            <StatTile
              label="Attention Dips"
              value={String(insights.dips.length)}
              accent={MODALITY_COLORS.dip}
              icon={<AlertTriangle className="w-4 h-4" />}
              testId="stat-dips"
            />
          </div>
        </div>

        <div className="flex items-center justify-center lg:pl-6 lg:border-l lg:border-card-border">
          <ResonanceScore value={meanResonance} />
        </div>
      </div>
    </section>
  );
}
