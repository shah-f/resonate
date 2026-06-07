# LLM Analysis Dry Run

This is a local placeholder. It proves the pipeline can build an LLM-ready artifact without calling OpenAI.

## What The Data Says

- Main story: The strongest combined activation arrives near the end, while the hook is weak.
- Strongest moment: {'timestep': 10, 'start': 10.0, 'end': 11.0, 'overall': 100.0, 'modalities': {'visual': 100.0, 'audio': 100.0, 'language': 100.0}}
- Weakest moment: {'timestep': 2, 'start': 2.0, 'end': 3.0, 'overall': 2.8, 'modalities': {'visual': 0.0, 'audio': 4.0, 'language': 4.5}}

## Human-Facing Insights We Could Give

- **Engagement Autopsy:** Predicted engagement drops around 1.0s. Strengthen the visual cue at this moment.
- **Payoff Timing:** The payoff appears to land late. Move the strongest idea, reveal, or contrast into the first 2-3 seconds.
- **Modality Balance:** Language-heavy: this clip is carried most by language signal. If the clip is too language-heavy, add visual proof, b-roll, captions with contrast, or clearer scene changes.
- **Cta Window:** Best local payoff/CTA moment is around 10.0-11.0s. Use this timing for payoff placement, or move this moment earlier if it lands too late for short-form retention.

## Data Richness

- Tribe event dataframe available: False
- Parcel names available: True

## Caveat

- This is not an LLM-generated final answer. Run without `--dry-run` after setting `OPENAI_API_KEY`.
