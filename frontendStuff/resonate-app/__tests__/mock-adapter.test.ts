import { insightsToResult } from "@/lib/mock-adapter";
import mockInsights from "@/lib/mock/insights.json";

describe("insightsToResult", () => {
  const result = insightsToResult(mockInsights);

  it("sets videoUrl to /demo-clip.mp4", () => {
    expect(result.videoUrl).toBe("/demo-clip.mp4");
  });

  it("sets duration from last segment end", () => {
    expect(result.duration).toBe(11);
  });

  it("maps segments unchanged", () => {
    expect(result.brain.segments[0]).toEqual({ start: 0, end: 1 });
    expect(result.brain.segments).toHaveLength(11);
  });

  it("maps normalizedTracks to both modality and normalizedTracks", () => {
    expect(result.brain.modality).toEqual(result.brain.normalizedTracks);
    expect(result.brain.modality.visual).toHaveLength(11);
    expect(result.brain.modality.audio).toHaveLength(11);
    expect(result.brain.modality.language).toHaveLength(11);
  });

  it("maps overall track", () => {
    expect(result.brain.overall).toHaveLength(11);
    expect(result.brain.overall[0]).toBeCloseTo(28.4, 1);
  });

  it("maps dips with camelCase fields", () => {
    expect(result.insights.dips.length).toBeGreaterThan(0);
    const dip = result.insights.dips[0];
    expect(dip.overallBefore).toBeCloseTo(28.4, 1);
    expect(dip.overallAfter).toBeCloseTo(10.7, 1);
    expect(dip.overallDelta).toBeCloseTo(-17.7, 1);
    expect(dip.leadModality).toBe("visual");
    expect(dip.modalityDeltas.visual).toBeCloseTo(-27.1, 1);
  });

  it("maps feature cards with camelCase suggestedFix", () => {
    const cards = result.insights.featureCards;
    expect(cards.engagementAutopsy.suggestedFix).toBeDefined();
    expect(cards.payoffTiming.suggestedFix).toBeDefined();
    expect(cards.modalityBalance.suggestedFix).toBeDefined();
    expect(cards.ctaWindow.suggestedFix).toBeDefined();
  });

  it("maps ctaWindow as a Moment (no note field)", () => {
    const cta = result.insights.ctaWindow;
    expect(cta.timestep).toBe(10);
    expect(cta.start).toBe(10);
    expect(cta.end).toBe(11);
    expect((cta as { note?: string }).note).toBeUndefined();
  });

  it("maps modalityBalance", () => {
    expect(result.insights.modalityBalance.dominant).toBe("language");
    expect(result.insights.modalityBalance.shares.visual).toBeCloseTo(13.5, 1);
  });

  it("maps windows", () => {
    expect(result.insights.windows.hook.label).toBe("0-3s hook");
    expect(result.insights.windows.hook.overall).toBeCloseTo(14.0, 1);
  });

  it("sets llmMarkdown to empty string", () => {
    expect(result.insights.llmMarkdown).toBe("");
  });

  it("maps caveats from notes array", () => {
    expect(result.insights.caveats.length).toBeGreaterThan(0);
    expect(typeof result.insights.caveats[0]).toBe("string");
  });
});
