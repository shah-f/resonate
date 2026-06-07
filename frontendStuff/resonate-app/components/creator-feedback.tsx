import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Card, CardContent } from '@/components/ui/card';

interface CreatorFeedbackProps {
  markdown: string;
  creatorInsights?: Array<{ title: string; detail: string }>;
}

export function CreatorFeedback({ markdown, creatorInsights }: CreatorFeedbackProps) {
  const hasMarkdown = markdown && markdown.trim().length > 0;
  const hasInsights = creatorInsights && creatorInsights.length > 0;

  if (!hasMarkdown && !hasInsights) return null;

  return (
    <Card className="bg-card border-card-border overflow-hidden" data-testid="panel-creator-feedback">
      <div className="bg-muted/30 border-b border-card-border p-4">
        <h3 className="label-mono text-xs text-muted-foreground">Analysis &amp; Creator Feedback</h3>
      </div>
      <CardContent className="p-6">
        {hasMarkdown ? (
          <article className="prose prose-invert prose-blue max-w-none prose-h2:text-white prose-h3:text-primary prose-a:text-primary hover:prose-a:text-primary/80">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {markdown}
            </ReactMarkdown>
          </article>
        ) : (
          <ul className="space-y-4">
            {creatorInsights!.map((insight, i) => (
              <li key={i} className="flex gap-3">
                <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                <div>
                  <p className="text-sm font-semibold text-white">{insight.title}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">{insight.detail}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
