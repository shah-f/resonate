import { FeatureCard as FeatureCardType, MODALITY_COLORS } from "@/lib/types";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Clock, Activity, Target } from "lucide-react";

interface FeatureCardProps {
  type: "engagementAutopsy" | "payoffTiming" | "modalityBalance" | "ctaWindow";
  card: FeatureCardType;
  onSeek: (time: number) => void;
}

export function FeatureCard({ type, card, onSeek }: FeatureCardProps) {
  const icons = {
    engagementAutopsy: <AlertCircle className="w-5 h-5" style={{ color: MODALITY_COLORS.dip }} />,
    payoffTiming: <Clock className="w-5 h-5" style={{ color: MODALITY_COLORS.strong }} />,
    modalityBalance: <Activity className="w-5 h-5 text-blue-400" />,
    ctaWindow: <Target className="w-5 h-5 text-green-400" />
  };

  const categoryLabels = {
    engagementAutopsy: "Engagement",
    payoffTiming: "Payoff",
    modalityBalance: "Balance",
    ctaWindow: "CTA Window"
  };

  // Attempt to parse a timestamp from the suggestedFix or evidence to make a jump button
  // Real implementation might have structured start/end in the card object.
  const extractTime = (text: string): number | null => {
    const match = text.match(/(\d+\.?\d*)s/);
    return match ? parseFloat(match[1]) : null;
  };

  const jumpTime = extractTime(card.suggestedFix) || extractTime(typeof card.evidence === 'string' ? card.evidence : '');

  return (
    <Card className="bg-card/50 border-card-border/50 hover:border-primary/30 transition-colors">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center gap-2">
          {icons[type]}
          <span className="label-mono text-[0.56rem] text-muted-foreground">{categoryLabels[type]}</span>
        </div>
        <h3 className="font-semibold text-white text-sm leading-snug" data-testid={`text-feature-headline-${type}`}>{card.headline}</h3>
        
        {typeof card.evidence === 'string' && card.evidence.trim() && (
          <div className="text-sm text-muted-foreground leading-relaxed break-words" data-testid={`text-feature-evidence-${type}`}>
            {card.evidence}
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