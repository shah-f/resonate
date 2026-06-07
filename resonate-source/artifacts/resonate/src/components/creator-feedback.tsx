import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardContent } from '@/components/ui/card';

interface CreatorFeedbackProps {
  markdown: string;
}

export function CreatorFeedback({ markdown }: CreatorFeedbackProps) {
  return (
    <Card className="bg-card border-card-border overflow-hidden" data-testid="panel-creator-feedback">
      <div className="bg-muted/30 border-b border-card-border p-4">
        <h3 className="text-lg font-medium text-white">Creator Feedback</h3>
      </div>
      <CardContent className="p-6">
        <article className="prose prose-invert prose-blue max-w-none prose-h2:text-white prose-h3:text-primary prose-a:text-primary hover:prose-a:text-primary/80">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {markdown}
          </ReactMarkdown>
        </article>
      </CardContent>
    </Card>
  );
}