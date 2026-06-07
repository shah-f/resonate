import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, ReferenceDot } from 'recharts';
import { ResonateResult, MODALITY_COLORS, Dip, Moment } from '@/lib/types';

interface AttentionTimelineProps {
  result: ResonateResult;
  currentTime: number;
  onSeek: (time: number) => void;
}

export function AttentionTimeline({ result, currentTime, onSeek }: AttentionTimelineProps) {
  const data = result.brain.segments.map((seg, i) => ({
    time: seg.start,
    displayTime: seg.start.toFixed(1) + 's',
    overall: result.brain.overall[i],
    visual: result.brain.modality.visual[i],
    audio: result.brain.modality.audio[i],
    language: result.brain.modality.language[i],
  }));

  const handleClick = (e: any) => {
    if (e && e.activePayload && e.activePayload.length > 0) {
      onSeek(e.activePayload[0].payload.time);
    }
  };

  const strongest = result.insights.rankedMoments.strongest[0];
  const maxTime = result.brain.segments[result.brain.segments.length - 1].end;

  return (
    <div className="w-full h-56 bg-card border border-card-border rounded-lg p-4 pb-2 relative flex flex-col" data-testid="chart-attention-timeline">
      <h3 className="text-sm font-medium text-muted-foreground mb-2">Overall Attention</h3>
      <div className="flex-1 min-h-0">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} onClick={handleClick} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
          <defs>
            <linearGradient id="colorOverall" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={MODALITY_COLORS.overall} stopOpacity={0.3}/>
              <stop offset="95%" stopColor={MODALITY_COLORS.overall} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis 
            dataKey="time" 
            type="number"
            domain={[0, maxTime]}
            stroke="#52525b" 
            fontSize={12} 
            tickMargin={10}
            minTickGap={20}
            tickFormatter={(val) => `${val}s`}
          />
          <YAxis 
            domain={[0, 1]} 
            stroke="#52525b" 
            fontSize={12}
            tickFormatter={(val) => (val * 100).toFixed(0) + '%'}
          />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const d = payload[0].payload;
                const dip = result.insights.dips.find(dp => Math.abs(dp.start - d.time) < 0.1);
                
                return (
                  <div className="bg-popover border border-popover-border p-3 rounded shadow-xl text-sm" data-testid="tooltip-timeline">
                    <p className="text-muted-foreground mb-1">{d.displayTime}</p>
                    <p className="font-medium text-white mb-2">Overall: {(d.overall * 100).toFixed(1)}%</p>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                      <span style={{ color: MODALITY_COLORS.visual }}>Vis: {(d.visual * 100).toFixed(0)}%</span>
                      <span style={{ color: MODALITY_COLORS.audio }}>Aud: {(d.audio * 100).toFixed(0)}%</span>
                      <span style={{ color: MODALITY_COLORS.language }}>Lang: {(d.language * 100).toFixed(0)}%</span>
                    </div>
                    {dip && (
                      <div className="mt-2 pt-2 border-t border-popover-border">
                        <span className="text-destructive font-medium flex items-center gap-1">
                          <span className="w-2 h-2 rounded-full bg-destructive inline-block"/>
                          Dip detected
                        </span>
                      </div>
                    )}
                  </div>
                );
              }
              return null;
            }} 
          />
          <Area 
            type="monotone" 
            dataKey="overall" 
            stroke={MODALITY_COLORS.overall} 
            fillOpacity={1} 
            fill="url(#colorOverall)" 
            strokeWidth={2}
            isAnimationActive={false}
          />
          
          {/* Playhead */}
          <ReferenceLine x={currentTime} stroke="#ffffff" strokeWidth={1} strokeDasharray="3 3" />
          
          {/* Dips */}
          {result.insights.dips.map((dip, i) => (
            <ReferenceLine 
              key={`dip-${i}`} 
              x={dip.start} 
              stroke={MODALITY_COLORS.dip} 
              strokeWidth={2} 
              strokeOpacity={0.8}
            />
          ))}
          
          {/* Strongest */}
          {strongest && (
            <ReferenceDot 
              x={strongest.start} 
              y={strongest.overall} 
              r={6} 
              fill={MODALITY_COLORS.strong} 
              stroke="#000" 
              strokeWidth={2} 
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}