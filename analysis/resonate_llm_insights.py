"""Generate polished creator-facing Resonate analysis with an LLM.

This script never calls Modal. It reads deterministic insights JSON, builds the
evidence prompt, and calls OpenAI to produce creator-facing markdown.

Use `--dry-run` only for local smoke tests.

Usage:
    python3 analysis/resonate_llm_insights.py results/finance_test_clip_insights.json --dry-run
    python3 analysis/resonate_llm_insights.py results/finance_test_clip_insights.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from resonate_llm_prompt import build_prompt


DEFAULT_MODEL = "gpt-4o"


def load_dotenv(path: Path = Path(".env")) -> None:
    """Tiny .env loader to avoid adding python-dotenv for this prototype."""
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def default_markdown_path(insights_path: Path) -> Path:
    return insights_path.with_name(f"{insights_path.stem}_llm_analysis.md")


def default_metadata_path(insights_path: Path) -> Path:
    return insights_path.with_name(f"{insights_path.stem}_llm_analysis.json")


def extract_response_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]

    chunks: list[str] = []
    for item in response.get("output", []) or []:
        for content in item.get("content", []) or []:
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    if chunks:
        return "\n".join(chunks).strip()

    raise ValueError("OpenAI response did not include output_text or output content text.")


def call_openai(prompt: str, model: str, temperature: float) -> tuple[str, dict[str, Any]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set. Use --dry-run or add it to .env.")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are Resonate's creator insight writer. Turn structured "
                    "predicted brain-response evidence into concise, careful, "
                    "actionable creator coaching."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    body = response.model_dump()
    return extract_response_text(body), body


def dry_run_analysis(insights: dict[str, Any]) -> str:
    evidence = insights.get("evidence_summary", {})
    cards = insights.get("feature_cards", {})
    llm_context = insights.get("llm_context", {})
    data_available = llm_context.get("input_data_available", {})

    lines = [
        "# LLM Analysis Dry Run",
        "",
        "This is a local placeholder. It proves the pipeline can build an LLM-ready artifact without calling OpenAI.",
        "",
        "## What The Data Says",
        "",
        f"- Main story: {evidence.get('main_story', 'No main story computed.')}",
        f"- Strongest moment: {evidence.get('strongest_moment')}",
        f"- Weakest moment: {evidence.get('weakest_moment')}",
        "",
        "## Human-Facing Insights We Could Give",
        "",
    ]
    for name, card in cards.items():
        lines.append(f"- **{name.replace('_', ' ').title()}:** {card.get('headline')} {card.get('suggested_fix')}")

    lines += [
        "",
        "## Data Richness",
        "",
        f"- Tribe event dataframe available: {data_available.get('tribe_event_dataframe', False)}",
        f"- Parcel names available: {data_available.get('parcel_names', False)}",
        "",
        "## Caveat",
        "",
        "- This is not an LLM-generated final answer. Run without `--dry-run` after setting `OPENAI_API_KEY`.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(
    markdown_path: Path,
    metadata_path: Path,
    analysis_text: str,
    *,
    model: str,
    dry_run: bool,
    prompt: str,
    raw_response: dict[str, Any] | None = None,
) -> None:
    markdown_path.write_text(analysis_text)
    metadata = {
        "model": model,
        "dry_run": dry_run,
        "markdown_path": str(markdown_path),
        "prompt_chars": len(prompt),
        "raw_response": raw_response,
    }
    with metadata_path.open("w") as f:
        json.dump(metadata, f, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate LLM creator insights from Resonate insights JSON.")
    parser.add_argument("insights_json", type=Path, help="Path to insights JSON from resonate_analysis.py.")
    parser.add_argument("--output", type=Path, help="Output markdown path.")
    parser.add_argument("--metadata-output", type=Path, help="Output metadata JSON path.")
    parser.add_argument("--model", default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--dry-run", action="store_true", help="Local smoke test only; skip OpenAI call.")
    args = parser.parse_args()

    load_dotenv()

    with args.insights_json.open() as f:
        insights = json.load(f)

    prompt = build_prompt(insights)
    markdown_path = args.output or default_markdown_path(args.insights_json)
    metadata_path = args.metadata_output or default_metadata_path(args.insights_json)

    if args.dry_run:
        analysis_text = dry_run_analysis(insights)
        raw_response = None
    else:
        analysis_text, raw_response = call_openai(prompt, args.model, args.temperature)

    write_outputs(
        markdown_path,
        metadata_path,
        analysis_text,
        model=args.model,
        dry_run=args.dry_run,
        prompt=prompt,
        raw_response=raw_response,
    )
    print(f"wrote {markdown_path}")
    print(f"wrote {metadata_path}")


if __name__ == "__main__":
    main()
