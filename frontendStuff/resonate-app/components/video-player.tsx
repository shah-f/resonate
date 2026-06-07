import { useRef, useEffect } from "react";

interface VideoPlayerProps {
  url: string;
  onTimeUpdate: (time: number) => void;
  seekTime: number | null;
}

export function VideoPlayer({ url, onTimeUpdate, seekTime }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (seekTime !== null && videoRef.current) {
      videoRef.current.currentTime = seekTime;
      // Optional: auto-play after seeking
      // videoRef.current.play().catch(() => {});
    }
  }, [seekTime]);

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      onTimeUpdate(videoRef.current.currentTime);
    }
  };

  return (
    <div className="w-full max-w-[320px] mx-auto rounded-2xl overflow-hidden border border-card-border bg-black relative aspect-[9/16] shadow-2xl">
      <video
        ref={videoRef}
        src={url}
        controls
        className="w-full h-full object-contain bg-black"
        onTimeUpdate={handleTimeUpdate}
        data-testid="video-player"
        crossOrigin="anonymous"
      />
    </div>
  );
}