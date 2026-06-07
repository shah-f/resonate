import { useState, useEffect } from 'react';
import { useParams } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { getStatus, getResult, getSampleResult } from '@/lib/mockApi';
import { ProcessingView } from '@/components/processing-view';
import { VideoPlayer } from '@/components/video-player';
import { BrainVisualization } from '@/components/brain-visualization';
import { AttentionTimeline } from '@/components/attention-timeline';
import { ModalityTracks } from '@/components/modality-tracks';
import { MainTakeaway } from '@/components/main-takeaway';
import { CreatorFeedback } from '@/components/creator-feedback';
import { FeatureCard } from '@/components/feature-card';
import { EvidenceDrawer } from '@/components/evidence-drawer';
import { Skeleton } from '@/components/ui/skeleton';

export default function Results() {
  const { jobId } = useParams<{ jobId: string }>();
  const isSample = jobId === 'sample';
  
  const [currentTime, setCurrentTime] = useState(0);
  const [seekTime, setSeekTime] = useState<number | null>(null);

  // Poll status if not sample
  const { data: statusData } = useQuery({
    queryKey: ['status', jobId],
    queryFn: () => getStatus(jobId!),
    enabled: !isSample && !!jobId,
    refetchInterval: (query) => {
      const isComplete = query.state.data?.status === 'complete' || query.state.data?.status === 'error';
      return isComplete ? false : 2000;
    },
  });

  // Fetch results when ready
  const isReady = isSample || statusData?.status === 'complete';
  const { data: result, isLoading: resultLoading } = useQuery({
    queryKey: ['result', jobId],
    queryFn: () => isSample ? getSampleResult() : getResult(jobId!),
    enabled: isReady,
  });

  if (!isSample && statusData?.status === 'error') {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4" data-testid="error-state">
          <h2 className="text-xl font-semibold">Analysis failed</h2>
          <p className="text-muted-foreground">
            {statusData.message ?? 'Something went wrong while analyzing your clip.'}
          </p>
          <a
            href={import.meta.env.BASE_URL}
            className="inline-block rounded-lg border border-card-border px-4 py-2 text-sm hover:bg-card transition-colors"
            data-testid="link-try-again"
          >
            Try another clip
          </a>
        </div>
      </div>
    );
  }

  if (!isSample && (!statusData || statusData.status !== 'complete')) {
    return (
      <ProcessingView 
        message={statusData?.message ?? 'Initializing...'} 
        progress={statusData?.progress ?? 0} 
      />
    );
  }

  if (result && (!result.brain?.segments || result.brain.segments.length === 0)) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4" data-testid="empty-state">
          <h2 className="text-xl font-semibold">No analysis available</h2>
          <p className="text-muted-foreground">This clip didn't return any timeline data.</p>
          <a
            href={import.meta.env.BASE_URL}
            className="inline-block rounded-lg border border-card-border px-4 py-2 text-sm hover:bg-card transition-colors"
          >
            Try another clip
          </a>
        </div>
      </div>
    );
  }

  if (resultLoading || !result) {
    return (
      <div className="min-h-screen bg-background p-6 space-y-6">
        <Skeleton className="h-[200px] w-full rounded-xl bg-card border-card-border" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-[500px] rounded-xl bg-card border-card-border" />
          <Skeleton className="h-[500px] rounded-xl bg-card border-card-border" />
        </div>
      </div>
    );
  }

  const handleSeek = (time: number) => {
    setSeekTime(time);
    // Reset seekTime so it can be re-triggered
    setTimeout(() => setSeekTime(null), 100);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <main className="max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        {/* Top summary */}
        <MainTakeaway result={result} />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Video + Charts */}
          <div className="lg:col-span-5 space-y-6 flex flex-col">
            <VideoPlayer 
              url={result.videoUrl} 
              onTimeUpdate={setCurrentTime} 
              seekTime={seekTime}
            />
            <div className="space-y-4">
              <AttentionTimeline result={result} currentTime={currentTime} onSeek={handleSeek} />
              <ModalityTracks result={result} currentTime={currentTime} onSeek={handleSeek} />
            </div>
          </div>

          {/* Right Column: Brain + Feature Cards */}
          <div className="lg:col-span-7 space-y-6">
            <div className="h-[480px]">
              <BrainVisualization result={result} currentTime={currentTime} />
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FeatureCard type="engagementAutopsy" card={result.insights.featureCards.engagementAutopsy} onSeek={handleSeek} />
              <FeatureCard type="payoffTiming" card={result.insights.featureCards.payoffTiming} onSeek={handleSeek} />
              <FeatureCard type="modalityBalance" card={result.insights.featureCards.modalityBalance} onSeek={handleSeek} />
              <FeatureCard type="ctaWindow" card={result.insights.featureCards.ctaWindow} onSeek={handleSeek} />
            </div>
          </div>
        </div>

        {/* Bottom Column: LLM Analysis */}
        <div className="mt-12 max-w-4xl mx-auto">
          <CreatorFeedback markdown={result.insights.llmMarkdown} />
          <EvidenceDrawer result={result} />
        </div>
      </main>
    </div>
  );
}