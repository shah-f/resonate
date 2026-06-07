import { ResonateResult, MODALITY_COLORS } from '@/lib/types';
import { Card, CardContent } from '@/components/ui/card';
import { ArrowUpRight, TrendingDown } from 'lucide-react';

interface MainTakeawayProps {
  result: ResonateResult;
}

export function MainTakeaway({ result }: MainTakeawayProps) {
  const { insights } = result;
  
  const strongest = insights.rankedMoments.strongest[0];
  const weakest = insights.rankedMoments.weakest[0];
  const dominant = insights.modalityBalance.dominant;

  return (
    <Card className="bg-card/50 border-card-border" data-testid="panel-main-takeaway">
      <CardContent className="p-4 sm:p-6">
        <h2 className="text-xl font-medium text-white mb-4">
          The payoff lands late: the strongest predicted response is at {strongest.start.toFixed(1)}-{strongest.end.toFixed(1)}s, while the hook stays low.
        </h2>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Strongest Moment</p>
            <p className="text-lg font-medium text-white flex items-center gap-1">
              {strongest.start.toFixed(1)}s <ArrowUpRight className="w-4 h-4" style={{ color: MODALITY_COLORS.strong }}/>
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Weakest Moment</p>
            <p className="text-lg font-medium text-white flex items-center gap-1">
              {weakest.start.toFixed(1)}s <TrendingDown className="w-4 h-4 text-destructive"/>
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Dominant Signal</p>
            <p className="text-lg font-medium capitalize" style={{ color: MODALITY_COLORS[dominant] }}>
              {dominant}
            </p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Attention Dips</p>
            <p className="text-lg font-medium text-white">
              {insights.dips.length}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}