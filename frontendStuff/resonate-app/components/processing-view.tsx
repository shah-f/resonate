import { Progress } from "@/components/ui/progress";
import { BrainCircuit } from "lucide-react";
import { useEffect, useState } from "react";

export function ProcessingView({ message, progress }: { message: string; progress: number }) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    const i = setInterval(() => setPulse(p => !p), 1000);
    return () => clearInterval(i);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full flex flex-col items-center space-y-12">
        <div className="relative">
          <div className={`absolute inset-0 bg-primary/20 rounded-full blur-3xl transition-opacity duration-1000 ${pulse ? 'opacity-100' : 'opacity-40'}`} />
          <BrainCircuit className="w-24 h-24 text-primary relative z-10 animate-pulse" />
        </div>
        
        <div className="w-full space-y-4 text-center">
          <p className="label-mono text-[0.6rem] text-primary text-glow">Predicting Brain Response</p>
          <h2 className="text-2xl font-medium text-white tracking-wide" data-testid="text-processing-message">
            {message}
          </h2>
          <Progress value={progress * 100} className="h-1 bg-muted" data-testid="progress-analysis" />
          <p className="readout text-xs text-muted-foreground">{Math.round(progress * 100)}%</p>
        </div>
      </div>
    </div>
  );
}