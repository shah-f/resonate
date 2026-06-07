"""Convert a Resonate insights JSON (0-100 scale) to the ResonateResult shape (0-1 scale)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _n(v: float | None) -> float | None:
    """Normalize a 0-100 score to 0-1, preserving None."""
    if v is None:
        return None
    return round(float(v) / 100.0, 4)


def _to_moment(m: dict) -> dict:
    return {
        "timestep": m["timestep"],
        "start": m["start"],
        "end": m["end"],
        "overall": _n(m["overall"]),
        "modalities": {k: _n(v) for k, v in m["modalities"].items()},
    }


def _to_dip(d: dict) -> dict:
    return {
        "timestep": d["timestep"],
        "start": d["start"],
        "end": d["end"],
        "overallBefore": _n(d["overall_before"]),
        "overallAfter": _n(d["overall_after"]),
        "overallDelta": _n(d["overall_delta"]),
        "leadModality": d["lead_modality"],
        "modalityDeltas": {k: _n(v) for k, v in d["modality_deltas"].items()},
    }


def _to_window(w: dict) -> dict:
    return {
        "label": w["label"],
        "indices": w["indices"],
        "overall": _n(w["overall"]),
        "modalities": {k: _n(v) for k, v in w["modalities"].items()},
    }


def _to_feature_card(fc: dict) -> dict:
    return {
        "headline": fc.get("headline", ""),
        "evidence": fc.get("evidence"),
        "suggestedFix": fc.get("suggested_fix", ""),
    }


def insights_to_result(
    insights: dict,
    video_url: str,
    llm_markdown: str = "",
    parcels: list | None = None,
    parcel_names: list | None = None,
    modality_indices: dict | None = None,
) -> dict:
    """Convert insights JSON → ResonateResult shape for the frontend."""
    segments = insights["segments"]
    duration = float(segments[-1]["end"]) if segments else 10.0

    norm = insights["normalized_tracks"]
    modality = {
        "visual": [_n(v) for v in norm["visual"]],
        "audio": [_n(v) for v in norm["audio"]],
        "language": [_n(v) for v in norm["language"]],
    }
    overall = [_n(v) for v in insights["overall"]]

    fc = insights.get("feature_cards", {})
    feature_cards: dict[str, Any] = {
        "engagementAutopsy": _to_feature_card(fc.get("engagement_autopsy", {})),
        "payoffTiming": _to_feature_card(fc.get("payoff_timing", {})),
        "modalityBalance": _to_feature_card(fc.get("modality_balance", {})),
        "ctaWindow": _to_feature_card(fc.get("cta_window", {})),
    }
    if "hook" in fc:
        feature_cards["hook"] = _to_feature_card(fc["hook"])

    cta_raw = insights["cta_window"]
    cta_window = {
        **_to_moment(cta_raw),
        "pctThroughClip": cta_raw.get("pct_through_clip"),
        "tooLate": cta_raw.get("too_late", False),
        "note": cta_raw.get("note", ""),
    }

    source = insights.get("source", "")
    filename = Path(source).name.replace("_insights.json", "").replace(".json", "")

    brain: dict[str, Any] = {
        "segments": segments,
        "modality": modality,
        "normalizedTracks": modality,
        "overall": overall,
    }
    if parcels is not None:
        brain["parcels"] = parcels
    if parcel_names is not None:
        brain["parcelNames"] = parcel_names
    if modality_indices is not None:
        brain["modalityIndices"] = modality_indices

    return {
        "videoUrl": video_url,
        "filename": filename,
        "duration": duration,
        "brain": brain,
        "insights": {
            "windows": {
                "hook": _to_window(insights["windows"]["hook"]),
                "middle": _to_window(insights["windows"]["middle"]),
                "close": _to_window(insights["windows"]["close"]),
            },
            "rankedMoments": {
                "strongest": [_to_moment(m) for m in insights["ranked_moments"]["strongest"]],
                "weakest": [_to_moment(m) for m in insights["ranked_moments"]["weakest"]],
            },
            "dips": [_to_dip(d) for d in insights["dips"]],
            "ctaWindow": cta_window,
            "modalityBalance": insights["modality_balance"],
            "featureCards": feature_cards,
            "llmMarkdown": llm_markdown,
            "caveats": insights.get("notes", []),
            "evidenceSummary": insights.get("evidence_summary", {}),
            "creatorInsights": insights.get("creator_insights", []),
        },
    }


if __name__ == "__main__":
    import sys
    insights_path = Path(sys.argv[1])
    video_url = sys.argv[2] if len(sys.argv) > 2 else "/sample.mp4"
    llm_md = Path(sys.argv[3]).read_text() if len(sys.argv) > 3 else ""
    parcel_json_path = Path(sys.argv[4]) if len(sys.argv) > 4 else None
    parcels = parcel_names = modality_indices = None
    if parcel_json_path and parcel_json_path.exists():
        pd = json.loads(parcel_json_path.read_text())
        parcels = pd.get("parcels")
        parcel_names = pd.get("parcel_names")
        modality_indices = pd.get("modality_indices")
    result = insights_to_result(
        json.loads(insights_path.read_text()), video_url, llm_md,
        parcels=parcels, parcel_names=parcel_names, modality_indices=modality_indices,
    )
    print(json.dumps(result, indent=2))
