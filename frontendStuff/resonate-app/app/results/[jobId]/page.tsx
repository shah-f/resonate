"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import type { ResonateResult } from "@/lib/types";

type StatusResponse = {
  status: "queued" | "processing" | "complete" | "error";
  message?: string;
};

export default function ResultsPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [status, setStatus] = useState<StatusResponse>({ status: "queued" });
  const [result, setResult] = useState<ResonateResult | null>(null);

  useEffect(() => {
    if (status.status === "complete" || status.status === "error") return;

    const interval = setInterval(async () => {
      const res = await fetch(`/api/status/${jobId}`);
      const data: StatusResponse = await res.json();
      setStatus(data);

      if (data.status === "complete") {
        clearInterval(interval);
        const r = await fetch(`/api/results/${jobId}`);
        setResult(await r.json());
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, status.status]);

  if (!result) {
    return (
      /* Esha: replace with your processing/loading component */
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-gray-300 animate-pulse">
          {status.message ?? "Initializing..."}
        </p>
      </main>
    );
  }

  return (
    /* Esha: replace each section with your styled components */
    <main className="min-h-screen p-6 flex flex-col gap-6">

      {/* Video Player — props: src={result.videoUrl} */}
      <section data-slot="video-player">
        <video src={result.videoUrl} controls className="w-full max-w-md" />
      </section>

      {/* Main Takeaway — props: rankedMoments={result.insights.rankedMoments}, modalityBalance={result.insights.modalityBalance} */}
      <section data-slot="main-takeaway" />

      {/* Attention Timeline — props: overall={result.brain.overall}, segments={result.brain.segments}, dips={result.insights.dips} */}
      <section data-slot="attention-timeline" />

      {/* Modality Tracks — props: modality={result.brain.modality} */}
      <section data-slot="modality-tracks" />

      {/* Feature Cards — props: featureCards={result.insights.featureCards} */}
      <section data-slot="feature-cards" />

      {/* LLM Analysis — props: markdown={result.insights.llmMarkdown} */}
      <section data-slot="llm-analysis" />

      {/* Brain/Modality Panel — props: modalityBalance={result.insights.modalityBalance} */}
      <section data-slot="modality-panel" />

      {/* Evidence Drawer — collapsible debug panel for judges */}
      <details className="text-xs text-gray-500">
        <summary className="cursor-pointer">Evidence</summary>
        <pre className="mt-2 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
      </details>

    </main>
  );
}
