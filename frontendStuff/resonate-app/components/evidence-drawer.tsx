import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { ResonateResult } from '@/lib/types';
import { AlertCircle } from 'lucide-react';

interface EvidenceDrawerProps {
  result: ResonateResult;
}

export function EvidenceDrawer({ result }: EvidenceDrawerProps) {
  return (
    <div className="mt-8 pt-8 border-t border-card-border" data-testid="panel-evidence-drawer">
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="evidence" className="border-card-border">
          <AccordionTrigger className="label-mono text-[0.7rem] text-muted-foreground hover:text-white">
            Debug & Evidence Drawer
          </AccordionTrigger>
          <AccordionContent className="space-y-4 pt-4">
            <div className="bg-muted/20 p-4 rounded-md border border-card-border space-y-2">
              <h4 className="label-mono text-[0.68rem] text-white flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-primary" /> 
                Analysis Caveats
              </h4>
              <ul className="list-disc pl-5 space-y-1 text-sm text-muted-foreground">
                {result.insights.caveats.map((caveat, i) => (
                  <li key={i}>{caveat}</li>
                ))}
              </ul>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-card p-4 rounded-md border border-card-border">
                <h4 className="label-mono text-[0.68rem] text-white mb-2">Raw Timings (s)</h4>
                <div className="h-32 overflow-y-auto text-xs text-muted-foreground space-y-1 font-mono">
                  {result.brain.segments.map((s, i) => (
                    <div key={i} className="flex justify-between border-b border-card-border/50 py-1">
                      <span>[{s.start.toFixed(2)} - {s.end.toFixed(2)}]</span>
                      <span>Ovr: {(result.brain.overall[i] * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="bg-card p-4 rounded-md border border-card-border">
                <h4 className="label-mono text-[0.68rem] text-white mb-2">Modality Balance</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="label-mono text-[0.6rem] text-muted-foreground">Visual Share</span>
                    <span className="readout text-blue-400">{(result.insights.modalityBalance.shares.visual * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="label-mono text-[0.6rem] text-muted-foreground">Audio Share</span>
                    <span className="readout text-green-400">{(result.insights.modalityBalance.shares.audio * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="label-mono text-[0.6rem] text-muted-foreground">Language Share</span>
                    <span className="readout text-rose-400">{(result.insights.modalityBalance.shares.language * 100).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}