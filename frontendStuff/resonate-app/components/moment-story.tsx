import { ResonateResult, MODALITY_COLORS, Modality } from '@/lib/types';
import { Button } from '@/components/ui/button';
import { ArrowUpRight, TrendingDown } from 'lucide-react';

interface MomentStoryProps {
  result: ResonateResult;
  onSeek: (time: number) => void;
}

type Phase = {
  key: string;
  label: string;
  overall: number;
  start: number;
  end: number;
  dominant: Modality;
};

type StoryEvent = {
  time: number;
  kind: 'peak' | 'dip';
  title: string;
  detail: string;
};

function dominantOf(mods: { visual: number | null; audio: number | null; language: number | null }): Modality {
  const entries: [Modality, number][] = [
    ['visual', mods.visual ?? 0],
    ['audio', mods.audio ?? 0],
    ['language', mods.language ?? 0],
  ];
  return entries.sort((a, b) => b[1] - a[1])[0][0];
}

export function MomentStory({ result, onSeek }: MomentStoryProps) {
  const { insights, brain } = result;
  const segments = brain.segments;

  const phases: Phase[] = (['hook', 'middle', 'close'] as const).map((key) => {
    const w = insights.windows[key];
    const first = segments[w.indices[0]];
    const last = segments[w.indices[w.indices.length - 1]];
    return {
      key,
      label: w.label,
      overall: w.overall ?? 0,
      start: first?.start ?? 0,
      end: last?.end ?? 0,
      dominant: dominantOf(w.modalities),
    };
  });

  const peak = insights.rankedMoments.strongest[0];
  const events: StoryEvent[] = [
    ...insights.dips.map((dip) => ({
      time: dip.start,
      kind: 'dip' as const,
      title: `Attention drops ${Math.round(dip.overallDelta * 100)}%`,
      detail: `${dip.leadModality.charAt(0).toUpperCase() + dip.leadModality.slice(1)} channel leads the fall.`,
    })),
    {
      time: peak.start,
      kind: 'peak' as const,
      title: `Peak response (${Math.round(peak.overall * 100)}%)`,
      detail: 'Strongest predicted brain response — your natural CTA window.',
    },
  ].sort((a, b) => a.time - b.time);

  return (
    <section data-testid="section-moment-story">
      <div className="flex items-center gap-3 mb-4">
        <span className="label-mono text-[0.6rem] text-primary">Moment by moment</span>
        <span className="h-px flex-1 bg-card-border" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-px bg-card-border border border-card-border mb-4">
        {phases.map((phase) => {
          const pct = Math.round(phase.overall * 100);
          return (
            <button
              key={phase.key}
              type="button"
              onClick={() => onSeek(phase.start)}
              data-testid={`phase-${phase.key}`}
              className="group flex flex-col gap-3 p-4 text-left bg-card/40 hover:bg-card/70 transition-colors"
            >
              <div className="flex items-center justify-between">
                <span className="label-mono text-[0.56rem] text-white">{phase.label}</span>
                <span className="label-mono text-[0.52rem] text-muted-foreground">
                  {phase.start.toFixed(1)}–{phase.end.toFixed(1)}s
                </span>
              </div>
              <div className="flex items-end gap-2">
                <span className="readout text-2xl text-white leading-none">{pct}%</span>
                <span
                  className="label-mono text-[0.5rem] mb-1 capitalize"
                  style={{ color: MODALITY_COLORS[phase.dominant] }}
                >
                  {phase.dominant}
                </span>
              </div>
              <div className="h-1.5 w-full bg-black/40 overflow-hidden">
                <div
                  className="h-full"
                  style={{
                    width: `${pct}%`,
                    background: MODALITY_COLORS.overall,
                  }}
                />
              </div>
            </button>
          );
        })}
      </div>

      <div className="border border-card-border bg-card/30 divide-y divide-card-border">
        {events.map((event, i) => {
          const accent = event.kind === 'peak' ? MODALITY_COLORS.strong : MODALITY_COLORS.dip;
          return (
            <div
              key={i}
              className="flex items-center gap-4 p-3 sm:p-4"
              data-testid={`event-${event.kind}-${i}`}
            >
              <span className="readout text-sm text-white w-12 shrink-0">{event.time.toFixed(1)}s</span>
              <span
                className="flex items-center justify-center w-7 h-7 shrink-0 border"
                style={{ borderColor: accent, color: accent }}
              >
                {event.kind === 'peak' ? (
                  <ArrowUpRight className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
              </span>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white font-medium leading-snug">{event.title}</p>
                <p className="text-xs text-muted-foreground leading-snug">{event.detail}</p>
              </div>
              <Button
                variant="secondary"
                size="sm"
                className="label-mono text-[0.56rem] h-8 bg-secondary/50 hover:bg-secondary shrink-0"
                onClick={() => onSeek(event.time)}
                data-testid={`button-event-jump-${i}`}
              >
                Jump
              </Button>
            </div>
          );
        })}
      </div>
    </section>
  );
}
