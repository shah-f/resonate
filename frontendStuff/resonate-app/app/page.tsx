"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud, Video, ArrowRight, Clock, Zap } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { CosmicBackdrop } from "@/components/cosmic-backdrop";
import { LIBRARY } from "@/lib/library";
import type { LibraryEntry } from "@/lib/library";

const MODALITY_ICON: Record<string, string> = { visual: "👁", audio: "🎵", language: "💬" };

export default function Home() {
  const router = useRouter();
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) setFile(acceptedFiles[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/mp4": [".mp4"], "video/quicktime": [".mov"], "video/webm": [".webm"] },
    maxFiles: 1,
  });

  const handleAnalyze = async () => {
    if (!file) return;
    try {
      setIsAnalyzing(true);
      const formData = new FormData();
      formData.append("video", file);
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      const { jobId } = await res.json();
      router.push(`/results/${jobId}`);
    } catch {
      toast({ title: "Upload failed", variant: "destructive" });
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
      <CosmicBackdrop />
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold tracking-tight text-white">Resonate</h1>
          <p className="text-xl text-muted-foreground">
            Find the moments your video loses the brain.
          </p>
        </div>

        <Card className="bg-card border-card-border overflow-hidden">
          <CardContent className="p-0">
            <div
              {...getRootProps()}
              className={`p-12 border-2 border-dashed transition-colors cursor-pointer flex flex-col items-center justify-center text-center gap-4 ${
                isDragActive
                  ? "border-primary bg-primary/5"
                  : "border-muted-border hover:border-primary/50 hover:bg-muted/20"
              }`}
            >
              <input {...getInputProps()} />
              {file ? (
                <>
                  <div className="h-16 w-16 rounded-full bg-primary/20 flex items-center justify-center mb-2">
                    <Video className="h-8 w-8 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-medium text-white">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-2">
                    <UploadCloud className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-medium text-white">
                      Drag &amp; drop your vertical video
                    </p>
                    <p className="text-sm text-muted-foreground">Supports .mp4, .mov, .webm</p>
                    <p className="text-xs text-primary mt-2">
                      Short vertical clips work best for the demo.
                    </p>
                  </div>
                </>
              )}
            </div>

            {file && (
              <div className="p-4 bg-muted/30 border-t border-card-border flex justify-end">
                <Button onClick={handleAnalyze} disabled={isAnalyzing} className="w-full sm:w-auto">
                  {isAnalyzing ? "Preparing..." : "Analyze Video"}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="space-y-3">
          <p className="text-center text-xs label-mono text-muted-foreground tracking-widest uppercase">
            Or browse pre-analyzed clips
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {LIBRARY.map((entry: LibraryEntry) => (
              <button
                key={entry.slug}
                onClick={() => router.push(`/results/${entry.slug}`)}
                className="flex items-center gap-3 rounded-xl border border-card-border bg-card/50 hover:bg-card hover:border-primary/40 transition-colors p-3 text-left group"
              >
                <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center text-lg shrink-0">
                  {MODALITY_ICON[entry.dominant] ?? "🎬"}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-white truncate group-hover:text-primary transition-colors">
                    {entry.title}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="flex items-center gap-1 text-[0.6rem] label-mono text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {entry.duration}s
                    </span>
                    <span className="flex items-center gap-1 text-[0.6rem] label-mono text-muted-foreground">
                      <Zap className="w-3 h-3" />
                      {entry.dominant}
                    </span>
                  </div>
                </div>
                <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
