import { FeatureCard as FeatureCardType, MODALITY_COLORS } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, Activity, Target, Zap } from "lucide-react";

interface FeatureCardProps {
  type: "engagementAutopsy" | "payoffTiming" | "modalityBalance" | "ctaWindow" | "hook";
  card: FeatureCardType;
  onSeek: (time: number) => void;
}

export function FeatureCard({ type, card, onSeek }: FeatureCardProps) {
  const icons = {
    hook: <Zap className="w-5 h-5 text-yellow-400" />,
    engagementAutopsy: <AlertCircle className="w-5 h-5" style={{ color: MODALITY_COLORS.dip }} />,
    payoffTiming: <Clock className="w-5 h-5" style={{ color: MODALITY_COLORS.strong }} />,
    modalityBalance: <Activity className="w-5 h-5 text-blue-400" />,
    ctaWindow: <Target className="w-5 h-5 text-green-400" />
  };

  const categoryLabels = {
    hook: "Hook",
    engagementAutopsy: "Engagement",
    payoffTiming: "Payoff",
    modalityBalance: "Balance",
    ctaWindow: "CTA Window"
  };

  // Extract jump time from structured evidence (start field) or fall back to text parsing
  const ev = card.evidence as Record<string, unknown> | null | undefined;
  const jumpTime: number | null = (() => {
    if (ev && typeof ev === 'object') {
      if (typeof ev.start === 'number') return ev.start;
      // hook card: first dip's start
      const dips = ev.hook_dips as Array<{ start: number }> | undefined;
      if (Array.isArray(dips) && dips.length > 0 && typeof dips[0].start === 'number') return dips[0].start;
    }
    return null;
  })();

  // Render structured evidence as key → value rows
  const evidenceRows: Array<{ label: string; value: string }> = (() => {
    if (!ev || typeof ev !== 'object') return [];
    const skip = new Set(['hook_dips', 'modality_deltas', 'hook_modalities', 'modalities', 'too_late', 'note']);
    return Object.entries(ev)
      .filter(([k, v]) => !skip.has(k) && (typeof v === 'number' || typeof v === 'string' || typeof v === 'boolean'))
      .map(([k, v]) => ({
        label: k.replace(/_/g, ' '),
        value: typeof v === 'number' ? (Number.isInteger(v) ? String(v) : v.toFixed(1)) : String(v),
      }));
  })();

  return (
    <Card className="bg-card/50 border-card-border/50 hover:border-primary/30 transition-colors">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center gap-2">
          {icons[type]}
          <span className="label-mono text-[0.56rem] text-muted-foreground">{categoryLabels[type]}</span>
        </div>
        <h3 className="font-semibold text-white text-sm leading-snug" data-testid={`text-feature-headline-${type}`}>{card.headline}</h3>

        {evidenceRows.length > 0 && (
          <div className="grid grid-cols-2 gap-x-3 gap-y-1" data-testid={`text-feature-evidence-${type}`}>
            {evidenceRows.map(({ label, value }) => (
              <div key={label} className="flex justify-between gap-1 text-[0.65rem]">
                <span className="text-muted-foreground truncate">{label}</span>
                <span className="text-white/80 font-mono shrink-0">{value}</span>
              </div>
            ))}
          </div>
        )}
        
        <div className="bg-muted/30 rounded p-3 text-sm text-white/90 border border-muted-border break-words" data-testid={`text-feature-fix-${type}`}>
          <span className="label-mono text-[0.56rem] text-primary mr-2">Fix</span>
          {card.suggestedFix}
        </div>

        {jumpTime !== null && (
          <Button 
            variant="secondary" 
            size="sm" 
            className="label-mono w-full mt-2 text-[0.6rem] h-8 bg-secondary/50 hover:bg-secondary"
            onClick={() => onSeek(jumpTime)}
            data-testid={`button-feature-jump-${type}`}
          >
            Jump to {jumpTime}s
          </Button>
        )}
      </CardContent>
    </Card>
  );
}