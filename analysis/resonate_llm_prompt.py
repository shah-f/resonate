"""Build a prompt for turning deterministic Resonate insights into human coaching.

This script does not call an LLM. It writes the exact prompt/evidence packet that an
LLM should receive later.

Usage:
    python3 analysis/resonate_llm_prompt.py results/finance_test_clip_insights.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def default_output_path(insights_path: Path) -> Path:
    return insights_path.with_name(f"{insights_path.stem}_llm_prompt.md")


def build_prompt(insights: dict) -> str:
    llm_context = insights["llm_context"]
    evidence = {
        "evidence_summary": insights.get("evidence_summary"),
        "feature_cards": insights.get("feature_cards"),
        "ranked_moments": insights.get("ranked_moments"),
        "windows": insights.get("windows"),
        "dips": insights.get("dips"),
        "cta_window": insights.get("cta_window"),
        "modality_balance": insights.get("modality_balance"),
        "parcel_evidence": llm_context.get("parcel_evidence"),
        "event_context": insights.get("event_context"),
        "notes": insights.get("notes"),
    }

    return f"""# Resonate LLM Analysis Prompt

You are writing creator-facing analysis for Resonate, a tool that uses predicted brain-response signals from video.

Write in the same style as the saved finance test clip analysis:

1. `What The Data Says`
2. `Human-Facing Insights We Could Give`
3. `Suggested Creator Feedback`
4. `Good Demo Cards For Resonate`
5. `Caveat`

Rules:

- Use only the evidence packet below.
- Say "predicted brain response", "signal suggests", or "model indicates"; do not say the data proves real viewer behavior.
- Scores are normalized within this clip. Do not call them universal retention percentages.
- Give concrete creator advice tied to timestamps, modalities, windows, or feature cards.
- If `event_context.available` is false, do not claim exact extracted event-row causes.
- Do not translate Schaefer parcel labels into precise named brain regions without a separate translation layer.
- Keep it concise, practical, and demo-ready.

Evidence packet:

```json
{json.dumps(evidence, indent=2)}
```

Now write the markdown analysis.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a prompt for LLM-based Resonate coaching.")
    parser.add_argument("insights_json", type=Path, help="Path to insights JSON from resonate_analysis.py.")
    parser.add_argument("--output", type=Path, help="Output markdown prompt path.")
    args = parser.parse_args()

    with args.insights_json.open() as f:
        insights = json.load(f)

    prompt = build_prompt(insights)
    output = args.output or default_output_path(args.insights_json)
    output.write_text(prompt)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
