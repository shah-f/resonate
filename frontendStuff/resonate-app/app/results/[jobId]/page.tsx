"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import type { ResonateResult, JobStatus } from "@/lib/types";
import { LIBRARY } from "@/lib/library";
import { ProcessingView } from "@/components/processing-view";
import { VideoPlayer } from "@/components/video-player";
import { AttentionTimeline } from "@/components/attention-timeline";
import { ModalityTracks } from "@/components/modality-tracks";
import { MissionHeader } from "@/components/mission-header";
import { MomentStory } from "@/components/moment-story";
import { CreatorFeedback } from "@/components/creator-feedback";
import { FeatureCard } from "@/components/feature-card";
import { EvidenceDrawer } from "@/components/evidence-drawer";
import { Skeleton } from "@/components/ui/skeleton";

// Three.js can't run on the server — lazy load it client-only
const BrainVisualization = dynamic(
  () => import("@/components/brain-visualization").then((m) => ({ default: m.BrainVisualization })),
  { ssr: false, loading: () => <Skeleton className="h-[480px] w-full rounded-xl bg-card" /> }
);

async function fetchStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`/api/status/${jobId}`);
  return res.json();
}

async function fetchResult(jobId: string): Promise<ResonateResult> {
  const res = await fetch(`/api/results/${jobId}`);
  return res.json();
}

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const router = useRouter();
  const isLibrary = LIBRARY.some((e) => e.slug === jobId);
  const isSample = jobId === "sample" || isLibrary;

  const [currentTime, setCurrentTime] = useState(0);
  const [seekTime, setSeekTime] = useState<number | null>(null);

  const { data: statusData } = useQuery({
    queryKey: ["status", jobId],
    queryFn: () => fetchStatus(jobId!),
    enabled: !isSample && !!jobId,
    refetchInterval: (query) => {
      const done =
        query.state.data?.status === "complete" || query.state.data?.status === "error";
      return done ? false : 2000;
    },
  });

  const isReady = isSample || statusData?.status === "complete";
  const { data: result, isLoading: resultLoading } = useQuery({
    queryKey: ["result", jobId],
    queryFn: () => fetchResult(jobId!),
    enabled: isReady,
  });

  if (!isSample && statusData?.status === "error") {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4">
          <h2 className="text-xl font-semibold">Analysis failed</h2>
          <p className="text-muted-foreground">
            {statusData.message ?? "Something went wrong while analyzing your clip."}
          </p>
          <button
            onClick={() => router.push("/")}
            className="inline-block rounded-lg border border-card-border px-4 py-2 text-sm hover:bg-card transition-colors"
          >
            Try another clip
          </button>
        </div>
      </div>
    );
  }

  if (!isSample && (!statusData || statusData.status !== "complete")) {
    return (
      <ProcessingView
        message={statusData?.message ?? "Initializing..."}
        progress={statusData?.progress ?? 0}
      />
    );
  }

  if (result && (!result.brain?.segments || result.brain.segments.length === 0)) {
    return (
      <div className="min-h-screen bg-background text-foreground flex items-center justify-center p-6">
        <div className="max-w-md text-center space-y-4">
          <h2 className="text-xl font-semibold">No analysis available</h2>
          <p className="text-muted-foreground">This clip didn&apos;t return any timeline data.</p>
          <button
            onClick={() => router.push("/")}
            className="inline-block rounded-lg border border-card-border px-4 py-2 text-sm hover:bg-card transition-colors"
          >
            Try another clip
          </button>
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
    setTimeout(() => setSeekTime(null), 100);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <main className="max-w-[1600px] mx-auto p-4 sm:p-6 lg:p-8 space-y-6">
        <MissionHeader result={result} onSeek={handleSeek} />
        <MomentStory result={result} onSeek={handleSeek} />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-5 space-y-6 flex flex-col">
            <VideoPlayer url={result.videoUrl} onTimeUpdate={setCurrentTime} seekTime={seekTime} />
            <div className="space-y-4">
              <AttentionTimeline result={result} currentTime={currentTime} onSeek={handleSeek} />
              <ModalityTracks result={result} currentTime={currentTime} onSeek={handleSeek} />
            </div>
          </div>

          <div className="lg:col-span-7 space-y-6">
            <div className="h-[480px]">
              <BrainVisualization result={result} currentTime={currentTime} />
            </div>
            <div className="space-y-4">
              {result.insights.featureCards.hook && (
                <FeatureCard type="hook" card={result.insights.featureCards.hook} onSeek={handleSeek} />
              )}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <FeatureCard type="engagementAutopsy" card={result.insights.featureCards.engagementAutopsy} onSeek={handleSeek} />
                <FeatureCard type="payoffTiming" card={result.insights.featureCards.payoffTiming} onSeek={handleSeek} />
                <FeatureCard type="modalityBalance" card={result.insights.featureCards.modalityBalance} onSeek={handleSeek} />
                <FeatureCard type="ctaWindow" card={result.insights.featureCards.ctaWindow} onSeek={handleSeek} />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-12 max-w-4xl mx-auto">
          <CreatorFeedback markdown={result.insights.llmMarkdown} />
          <EvidenceDrawer result={result} />
        </div>
      </main>
    </div>
  );
}
