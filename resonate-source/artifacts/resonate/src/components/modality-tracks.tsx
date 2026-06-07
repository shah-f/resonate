import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { ResonateResult, MODALITY_COLORS } from '@/lib/types';

interface ModalityTracksProps {
  result: ResonateResult;
  currentTime: number;
  onSeek: (time: number) => void;
}

export function ModalityTracks({ result, currentTime, onSeek }: ModalityTracksProps) {
  const data = result.brain.segments.map((seg, i) => ({
    time: seg.start,
    displayTime: seg.start.toFixed(1) + 's',
    visual: result.brain.normalizedTracks?.visual[i] ?? result.brain.modality.visual[i],
    audio: result.brain.normalizedTracks?.audio[i] ?? result.brain.modality.audio[i],
    language: result.brain.normalizedTracks?.language[i] ?? result.brain.modality.language[i],
  }));

  const handleClick = (e: any) => {
    if (e && e.activePayload && e.activePayload.length > 0) {
      onSeek(e.activePayload[0].payload.time);
    }
  };

  const maxTime = result.brain.segments[result.brain.segments.length - 1].end;

  return (
    <div className="w-full h-56 bg-card border border-card-border rounded-lg p-4 pb-2 relative flex flex-col" data-testid="chart-modality-tracks">
      <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
        <h3 className="text-sm font-medium text-muted-foreground">Modality Breakdown</h3>
        <div className="flex gap-3 text-xs">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{backgroundColor: MODALITY_COLORS.visual}}></span> Visual</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{backgroundColor: MODALITY_COLORS.audio}}></span> Audio</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{backgroundColor: MODALITY_COLORS.language}}></span> Language</span>
        </div>
      </div>
      <div className="flex-1 min-h-0">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} onClick={handleClick} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
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
            contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#fff' }}
            itemStyle={{ color: '#fff' }}
          />
          
          <Line type="monotone" dataKey="visual" stroke={MODALITY_COLORS.visual} strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="audio" stroke={MODALITY_COLORS.audio} strokeWidth={2} dot={false} isAnimationActive={false} />
          <Line type="monotone" dataKey="language" stroke={MODALITY_COLORS.language} strokeWidth={2} dot={false} isAnimationActive={false} />
          
          <ReferenceLine x={currentTime} stroke="#ffffff" strokeWidth={1} strokeDasharray="3 3" />
        </LineChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}