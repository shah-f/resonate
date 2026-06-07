import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useLocation } from "wouter";
import { analyzeVideo } from "@/lib/mockApi";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { UploadCloud, Video, ArrowRight } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export default function Home() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/mp4': ['.mp4'],
      'video/quicktime': ['.mov'],
      'video/webm': ['.webm']
    },
    maxFiles: 1
  });

  const handleAnalyze = async () => {
    if (!file) return;
    try {
      setIsAnalyzing(true);
      const { jobId } = await analyzeVideo(file);
      setLocation(`/results/${jobId}`);
    } catch (e) {
      toast({ title: "Upload failed", variant: "destructive" });
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col items-center justify-center p-6">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold tracking-tight text-white" data-testid="text-app-name">Resonate</h1>
          <p className="text-xl text-muted-foreground" data-testid="text-app-subtitle">
            Find the moments your video loses the brain.
          </p>
        </div>

        <Card className="bg-card border-card-border overflow-hidden">
          <CardContent className="p-0">
            <div 
              {...getRootProps()} 
              className={`p-12 border-2 border-dashed transition-colors cursor-pointer flex flex-col items-center justify-center text-center gap-4 ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted-border hover:border-primary/50 hover:bg-muted/20'}`}
              data-testid="area-upload-dropzone"
            >
              <input {...getInputProps()} data-testid="input-upload-video" />
              
              {file ? (
                <>
                  <div className="h-16 w-16 rounded-full bg-primary/20 flex items-center justify-center mb-2">
                    <Video className="h-8 w-8 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-medium text-white">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="h-16 w-16 rounded-full bg-muted flex items-center justify-center mb-2">
                    <UploadCloud className="h-8 w-8 text-muted-foreground" />
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-medium text-white">Drag & drop your vertical video</p>
                    <p className="text-sm text-muted-foreground">Supports .mp4, .mov, .webm</p>
                    <p className="text-xs text-primary mt-2">Short vertical clips work best for the demo.</p>
                  </div>
                </>
              )}
            </div>
            
            {file && (
              <div className="p-4 bg-muted/30 border-t border-card-border flex justify-end">
                <Button 
                  onClick={handleAnalyze} 
                  disabled={isAnalyzing}
                  className="w-full sm:w-auto"
                  data-testid="button-analyze-video"
                >
                  {isAnalyzing ? "Preparing..." : "Analyze Video"}
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="text-center">
          <Button 
            variant="link" 
            className="text-muted-foreground hover:text-white"
            onClick={() => setLocation('/results/sample')}
            data-testid="link-sample-clip"
          >
            Or try the sample clip without uploading
          </Button>
        </div>
      </div>
    </div>
  );
}