"""Convert a saved Resonate inference result into product-ready insights.

This is deterministic analysis code. It does not call Modal or an LLM.

Usage:
    python3 analysis/resonate_analysis.py results/finance_test_clip.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np


DEFAULT_MAPPING_PATH = Path("results/schaefer200_modality_mapping.json")
MODALITIES = ("visual", "audio", "language")


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return json.load(f)


def normalize(values: np.ndarray) -> np.ndarray:
    values = values.astype(float)
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return np.zeros_like(values, dtype=float)
    lo = float(finite.min())
    hi = float(finite.max())
    if math.isclose(lo, hi):
        return np.zeros_like(values, dtype=float)
    return (values - lo) / (hi - lo) * 100.0


def parse_segment(segment: Any, index: int) -> dict[str, float]:
    if isinstance(segment, dict):
        start = segment.get("start")
        end = segment.get("end")
        duration = segment.get("duration")
        if start is not None and end is not None:
            return {"start": float(start), "end": float(end)}
        if start is not None and duration is not None:
            start_f = float(start)
            return {"start": start_f, "end": start_f + float(duration)}

    text = str(segment)
    start_match = re.search(r"start=np\.float64\(([-+]?[0-9]*\.?[0-9]+)\)", text)
    duration_match = re.search(r"duration=([-+]?[0-9]*\.?[0-9]+)", text)
    if start_match and duration_match:
        start = float(start_match.group(1))
        return {"start": start, "end": start + float(duration_match.group(1))}

    return {"start": float(index), "end": float(index + 1)}


def get_segments(result: dict[str, Any], n_timesteps: int) -> list[dict[str, float]]:
    parsed = result.get("segments_parsed")
    if isinstance(parsed, list) and parsed:
        return [parse_segment(segment, i) for i, segment in enumerate(parsed)]

    raw = result.get("segments") or []
    if raw:
        return [parse_segment(segment, i) for i, segment in enumerate(raw)]

    return [{"start": float(i), "end": float(i + 1)} for i in range(n_timesteps)]


def get_tracks(result: dict[str, Any]) -> dict[str, np.ndarray]:
    modality = result.get("modality") or {}
    tracks = {}
    for name in MODALITIES:
        values = modality.get(name)
        if values is None:
            raise ValueError(f"Missing modality track: {name}")
        tracks[name] = np.asarray(values, dtype=float)
    return tracks


def window_indices(segments: list[dict[str, float]], start: float, end: float) -> list[int]:
    hits = []
    for i, segment in enumerate(segments):
        center = (segment["start"] + segment["end"]) / 2.0
        if start <= center < end:
            hits.append(i)
    return hits


def summarize_window(
    label: str,
    indices: list[int],
    normalized_tracks: dict[str, np.ndarray],
    overall: np.ndarray,
) -> dict[str, Any]:
    if not indices:
        return {
            "label": label,
            "indices": [],
            "overall": None,
            "modalities": {m: None for m in MODALITIES},
        }
    return {
        "label": label,
        "indices": indices,
        "overall": round(float(overall[indices].mean()), 1),
        "modalities": {
            m: round(float(normalized_tracks[m][indices].mean()), 1)
            for m in MODALITIES
        },
    }


def find_dips(
    overall: np.ndarray,
    normalized_tracks: dict[str, np.ndarray],
    segments: list[dict[str, float]],
) -> list[dict[str, Any]]:
    if overall.size < 2:
        return []

    drops = np.diff(overall)
    threshold = min(-12.0, float(drops.mean() - drops.std()))
    candidates = [i for i, drop in enumerate(drops) if drop <= threshold]

    # Always include the lowest moment if it is meaningfully below the average.
    lowest = int(overall.argmin())
    if float(overall.mean() - overall[lowest]) >= 15.0 and lowest > 0:
        candidates.append(lowest - 1)

    dips = []
    seen_targets = set()
    for start_idx in sorted(set(candidates)):
        target_idx = min(start_idx + 1, overall.size - 1)
        if target_idx in seen_targets:
            continue
        seen_targets.add(target_idx)
        modality_drops = {
            m: float(normalized_tracks[m][target_idx] - normalized_tracks[m][start_idx])
            for m in MODALITIES
        }
        lead_modality = min(modality_drops, key=modality_drops.get)
        segment = segments[target_idx]
        dips.append(
            {
                "timestep": target_idx,
                "start": round(float(segment["start"]), 3),
                "end": round(float(segment["end"]), 3),
                "overall_before": round(float(overall[start_idx]), 1),
                "overall_after": round(float(overall[target_idx]), 1),
                "overall_delta": round(float(overall[target_idx] - overall[start_idx]), 1),
                "lead_modality": lead_modality,
                "modality_deltas": {
                    m: round(delta, 1) for m, delta in modality_drops.items()
                },
            }
        )
    return dips


def modality_balance(tracks: dict[str, np.ndarray]) -> dict[str, Any]:
    minima = min(float(values.min()) for values in tracks.values())
    shifted = {m: values - minima + 1e-9 for m, values in tracks.items()}
    totals = {m: float(values.mean()) for m, values in shifted.items()}
    total = sum(totals.values())
    shares = {
        m: round((totals[m] / total * 100.0) if total else 0.0, 1)
        for m in MODALITIES
    }
    dominant = max(shares, key=shares.get)
    return {
        "shares": shares,
        "dominant": dominant,
        "verdict": f"{dominant.title()}-heavy: this clip is carried most by {dominant} signal.",
    }


def cta_window(overall: np.ndarray, normalized_tracks: dict[str, np.ndarray], segments: list[dict[str, float]]) -> dict[str, Any]:
    n = overall.size
    # Exclude the final 10% of the clip (min 1 timestep) to avoid recommending the last frame.
    cutoff = max(1, n - max(1, n // 10))
    early = overall[:cutoff]

    # Find the earliest local maximum above the 75th percentile in the early window.
    threshold = float(np.percentile(overall, 75))
    candidates = [
        i for i in range(1, cutoff - 1)
        if overall[i] >= threshold and overall[i] >= overall[i - 1] and overall[i] >= overall[i + 1]
    ]
    # Also consider the global max within the early window.
    early_max_idx = int(early.argmax())
    if early_max_idx not in candidates and float(early[early_max_idx]) >= threshold:
        candidates.append(early_max_idx)

    too_late = False
    if candidates:
        idx = min(candidates)  # earliest high-attention moment
    else:
        # No qualifying moment before the end — CTA is forced late.
        idx = int(overall.argmax())
        too_late = True

    segment = segments[idx]
    clip_end = segments[-1]["end"]
    pct_through = round(float(segments[idx]["start"]) / clip_end * 100) if clip_end else 0
    return {
        "timestep": idx,
        "start": round(float(segment["start"]), 3),
        "end": round(float(segment["end"]), 3),
        "overall": round(float(overall[idx]), 1),
        "modalities": {m: round(float(normalized_tracks[m][idx]), 1) for m in MODALITIES},
        "pct_through_clip": pct_through,
        "too_late": too_late,
        "note": (
            "No high-attention moment found before the final stretch — CTA window is too late for short-form retention."
            if too_late
            else "Earliest high-attention moment; ideal for payoff or CTA placement."
        ),
    }


def ranked_moments(
    overall: np.ndarray,
    normalized_tracks: dict[str, np.ndarray],
    segments: list[dict[str, float]],
) -> dict[str, list[dict[str, Any]]]:
    def moment(idx: int) -> dict[str, Any]:
        segment = segments[idx]
        return {
            "timestep": idx,
            "start": round(float(segment["start"]), 3),
            "end": round(float(segment["end"]), 3),
            "overall": round(float(overall[idx]), 1),
            "modalities": {
                m: round(float(normalized_tracks[m][idx]), 1)
                for m in MODALITIES
            },
        }

    strongest = np.argsort(overall)[-3:][::-1]
    weakest = np.argsort(overall)[:3]
    return {
        "strongest": [moment(int(i)) for i in strongest],
        "weakest": [moment(int(i)) for i in weakest],
    }


def parcel_movers(result: dict[str, Any], mapping: dict[str, Any] | None, top_n: int = 8) -> dict[str, Any] | None:
    parcels_raw = result.get("parcels")
    if not parcels_raw:
        return None
    parcels = np.asarray(parcels_raw, dtype=float)
    if parcels.ndim != 2 or parcels.shape[0] < 2:
        return None

    parcel_names = result.get("parcel_names") or (mapping or {}).get("parcel_names") or []
    if len(parcel_names) != parcels.shape[1]:
        parcel_names = [f"parcel_{i}" for i in range(parcels.shape[1])]

    hook_end = min(3, parcels.shape[0])
    close_start = max(0, parcels.shape[0] - 3)
    delta = parcels[close_start:].mean(axis=0) - parcels[:hook_end].mean(axis=0)

    def pack(indices: np.ndarray) -> list[dict[str, Any]]:
        return [
            {
                "parcel_index": int(i),
                "parcel_name": parcel_names[int(i)],
                "delta": round(float(delta[int(i)]), 4),
            }
            for i in indices
        ]

    rising = np.argsort(delta)[-top_n:][::-1]
    falling = np.argsort(delta)[:top_n]
    return {
        "comparison": "last_3_timesteps_minus_first_3_timesteps",
        "top_rising": pack(rising),
        "top_falling": pack(falling),
    }


def event_context(result: dict[str, Any], max_records: int = 8) -> dict[str, Any]:
    events = result.get("events") or {}
    records = events.get("records") or []
    columns = events.get("columns") or []
    return {
        "available": bool(records),
        "shape": events.get("shape"),
        "columns": columns,
        "sample_records": records[:max_records],
        "usage_note": (
            "Use these rows to ground explanations in extracted video/audio/text events."
            if records
            else "No Tribe event dataframe was saved for this result; do not claim event-row-specific causes."
        ),
    }


def evidence_summary(
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    cta: dict[str, Any],
    balance: dict[str, Any],
    moments: dict[str, list[dict[str, Any]]],
    overall: np.ndarray | None = None,
) -> dict[str, Any]:
    hook = windows["hook"]
    close = windows["close"]
    payoff_delta = None
    if hook["overall"] is not None and close["overall"] is not None:
        payoff_delta = round(float(close["overall"] - hook["overall"]), 1)

    slow_burn = is_slow_burn(overall) if overall is not None else False

    if slow_burn:
        main_story = "Slow-burn pattern: predicted activation rises across the entire clip, starting very low. The hook fails to capture attention before the 2s scroll threshold."
    elif payoff_delta is not None and payoff_delta >= 25:
        main_story = "The strongest combined activation arrives near the end, while the hook is weak."
    else:
        main_story = "The clip has uneven activation across time."

    return {
        "main_story": main_story,
        "slow_burn": slow_burn,
        "payoff_delta_close_minus_hook": payoff_delta,
        "cta_too_late": cta.get("too_late", False),
        "first_major_dip": dips[0] if dips else None,
        "strongest_moment": moments["strongest"][0] if moments["strongest"] else None,
        "weakest_moment": moments["weakest"][0] if moments["weakest"] else None,
        "cta_window": cta,
        "modality_balance": balance,
    }


def hook_card(windows: dict[str, Any], dips: list[dict[str, Any]]) -> dict[str, Any]:
    hook = windows["hook"]
    if hook["overall"] is None:
        return {
            "headline": "No hook data available.",
            "evidence": None,
            "suggested_fix": "Ensure the clip is long enough to capture a hook window.",
        }

    hook_dips = [d for d in dips if d["end"] <= 3.0]
    mods = hook["modalities"]
    lead = max(mods, key=lambda m: mods[m] if mods[m] is not None else -1)
    weak = min(mods, key=lambda m: mods[m] if mods[m] is not None else 999)

    if hook_dips:
        first = hook_dips[0]
        headline = (
            f"Hook collapses at {first['start']:.0f}s — predicted attention drops {abs(first['overall_delta']):.0f} pts, "
            f"led by {first['lead_modality']}."
        )
        fix = (
            f"Your hook scores {hook['overall']}/100 overall. "
            f"{lead.title()} is your strongest channel ({mods[lead]}/100) but {weak} is nearly absent ({mods[weak]}/100). "
            f"Add a strong {weak} cue in the first 2 seconds — a visual hook, key phrase, or sound that signals what the video is about."
        )
    else:
        headline = f"Hook scores {hook['overall']}/100 — room to improve before the 3s scroll threshold."
        fix = (
            f"{lead.title()} is your strongest hook channel ({mods[lead]}/100). "
            f"Lead with your most compelling {lead} cue in the first 2 seconds."
        )

    return {
        "headline": headline,
        "evidence": {
            "hook_overall": hook["overall"],
            "hook_modalities": mods,
            "hook_dips": hook_dips,
        },
        "suggested_fix": fix,
    }


def is_slow_burn(overall: np.ndarray) -> bool:
    """True when activation rises monotonically or near-monotonically across the clip."""
    if overall.size < 4:
        return False
    diffs = np.diff(overall)
    return float((diffs > 0).mean()) >= 0.75


def feature_cards(
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    cta: dict[str, Any],
    balance: dict[str, Any],
    overall: np.ndarray | None = None,
) -> dict[str, Any]:
    first_dip = dips[0] if dips else None
    hook = windows["hook"]
    close = windows["close"]
    payoff_delta = (
        round(float(close["overall"] - hook["overall"]), 1)
        if hook["overall"] is not None and close["overall"] is not None
        else None
    )

    slow_burn = is_slow_burn(overall) if overall is not None else False
    payoff_late = payoff_delta is not None and payoff_delta >= 25

    if slow_burn:
        payoff_headline = "Slow-burn pattern: predicted attention climbs across the entire clip but starts very low."
        payoff_fix = (
            "Move your strongest idea, reveal, or hook to the first 2–3 seconds. "
            "Short-form viewers decide to scroll within 2s — the payoff arriving at the end means most won't reach it."
        )
    elif payoff_late:
        payoff_headline = "The payoff appears to land late."
        payoff_fix = "Move the strongest idea, reveal, or contrast into the first 2-3 seconds."
    else:
        payoff_headline = "The payoff timing is not clearly late from this run."
        payoff_fix = "Compare against more clips to establish a baseline."

    return {
        "hook": hook_card(windows, dips),
        "engagement_autopsy": {
            "headline": (
                f"Predicted engagement drops around {first_dip['start']:.1f}s."
                if first_dip
                else "No major early engagement dip detected."
            ),
            "evidence": first_dip,
            "suggested_fix": (
                f"Strengthen the {first_dip['lead_modality']} cue at this moment."
                if first_dip
                else "Keep the current opening structure, then compare against more clips."
            ),
        },
        "payoff_timing": {
            "headline": payoff_headline,
            "evidence": {
                "hook_overall": hook["overall"],
                "close_overall": close["overall"],
                "close_minus_hook": payoff_delta,
                "slow_burn": slow_burn,
            },
            "suggested_fix": payoff_fix,
        },
        "modality_balance": {
            "headline": balance["verdict"],
            "evidence": balance["shares"],
            "suggested_fix": (
                "If the clip is too language-heavy, add visual proof, b-roll, captions with contrast, or clearer scene changes."
                if balance["dominant"] == "language"
                else "Support the dominant modality with clearer visual, audio, and language cues."
            ),
        },
        "cta_window": {
            "headline": (
                f"No strong CTA window found before the final stretch — attention peaks too late."
                if cta.get("too_late")
                else f"Best CTA moment is around {cta['start']:.1f}–{cta['end']:.1f}s ({cta.get('pct_through_clip', '?')}% through the clip)."
            ),
            "evidence": cta,
            "suggested_fix": (
                "Restructure so a high-attention moment lands in the middle third of the clip — that's where CTA placement works for short-form."
                if cta.get("too_late")
                else "Place your payoff or CTA call here. If this moment is too early, it signals the clip has good structure."
            ),
        },
    }


def creator_insights(
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    balance: dict[str, Any],
    cta: dict[str, Any],
    overall: np.ndarray | None = None,
) -> list[dict[str, str]]:
    insights = []

    hook = windows["hook"]
    close = windows["close"]
    slow_burn = is_slow_burn(overall) if overall is not None else False

    if slow_burn:
        insights.append(
            {
                "title": "Slow-burn pattern — hook is too weak",
                "detail": (
                    f"Predicted attention rises across the entire clip (hook: {hook['overall']}/100 → close: {close['overall']}/100). "
                    "Short-form viewers scroll within 2s. Move the strongest moment to the opening."
                ),
            }
        )
    elif hook["overall"] is not None and close["overall"] is not None and close["overall"] - hook["overall"] >= 25:
        insights.append(
            {
                "title": "The payoff arrives late",
                "detail": (
                    f"The close scores {close['overall']}/100 while the hook scores "
                    f"{hook['overall']}/100. Move the strongest idea earlier."
                ),
            }
        )

    # Hook modality breakdown — surface which channel is carrying vs. missing the hook.
    if hook["overall"] is not None:
        mods = hook["modalities"]
        lead = max(mods, key=lambda m: mods[m] if mods[m] is not None else -1)
        weak = min(mods, key=lambda m: mods[m] if mods[m] is not None else 999)
        if mods[weak] is not None and mods[lead] is not None and mods[lead] - mods[weak] >= 15:
            insights.append(
                {
                    "title": f"Hook is {lead}-led, {weak} is nearly absent",
                    "detail": (
                        f"In the first 3s: {lead}={mods[lead]}/100, {weak}={mods[weak]}/100. "
                        f"Add a {weak} cue early — a visual hook, key phrase, or audio signal — "
                        "to engage viewers across all channels before they scroll."
                    ),
                }
            )

    hook_dips = [d for d in dips if d["end"] <= 3.0]
    mid_dips = [d for d in dips if d["start"] >= 3.0]
    for dip_group, label in ((hook_dips, "hook"), (mid_dips, "mid-video")):
        if dip_group:
            first = dip_group[0]
            insights.append(
                {
                    "title": f"Attention dip at {first['start']:.1f}s ({label})",
                    "detail": (
                        f"Overall signal drops {abs(first['overall_delta']):.0f} pts, led by "
                        f"{first['lead_modality']} (−{abs(first['modality_deltas'][first['lead_modality']]):.0f} pts)."
                    ),
                }
            )

    insights.append(
        {
            "title": "Modality balance",
            "detail": balance["verdict"],
        }
    )

    if cta.get("too_late"):
        insights.append(
            {
                "title": "No CTA window before the end",
                "detail": "No high-attention moment was found before the final stretch. Restructure so a strong moment lands in the middle third of the clip.",
            }
        )
    else:
        insights.append(
            {
                "title": "Best payoff window",
                "detail": f"Strongest early high-attention moment is around {cta['start']:.1f}–{cta['end']:.1f}s ({cta.get('pct_through_clip', '?')}% through).",
            }
        )
    return insights


def llm_context(
    result_path: Path,
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    cta: dict[str, Any],
    balance: dict[str, Any],
    moments: dict[str, list[dict[str, Any]]],
    cards: dict[str, Any],
    movers: dict[str, Any] | None,
    result: dict[str, Any],
) -> dict[str, Any]:
    event_info = result.get("events") or {}
    has_events = bool(event_info.get("records"))
    events = event_context(result)
    return {
        "purpose": "Use this evidence packet to write creator-facing coaching. Do not invent facts beyond the structured evidence.",
        "source": str(result_path),
        "input_data_available": {
            "modality_tracks": True,
            "overall_curve": True,
            "segments": True,
            "parcels": bool(result.get("parcels")),
            "parcel_names": bool(result.get("parcel_names")) or bool(movers),
            "tribe_event_dataframe": has_events,
        },
        "feature_cards": cards,
        "ranked_moments": moments,
        "window_summary": windows,
        "dips": dips,
        "cta_window": cta,
        "modality_balance": balance,
        "event_context": events,
        "parcel_evidence": {
            "top_rising": (movers or {}).get("top_rising", [])[:5],
            "top_falling": (movers or {}).get("top_falling", [])[:5],
            "usage_note": "Use parcel labels as supporting atlas evidence only; do not translate them into precise named brain regions without a separate translation layer.",
        },
        "recommended_language_rules": [
            "Say 'predicted brain response' or 'signal suggests', not 'proves viewers will drop'.",
            "Scores are normalized within this clip; do not describe them as universal retention percentages.",
            "When giving a fix, tie it to a timestamp, modality, or window from the evidence.",
            "If event dataframe records are unavailable, do not claim exact source event text/audio/video rows.",
        ],
        "output_style": {
            "match_reference": "Use the same shape as results/finance_test_clip_analysis.md.",
            "sections": [
                "What The Data Says",
                "Human-Facing Insights We Could Give",
                "Suggested Creator Feedback",
                "Good Demo Cards For Resonate",
                "Caveat",
            ],
            "tone": "Clear, concrete, creator-facing, careful about uncertainty.",
        },
        "prompt_skeleton": (
            "Write a concise markdown analysis with sections: What The Data Says, "
            "Human-Facing Insights We Could Give, Suggested Creator Feedback, "
            "Good Demo Cards For Resonate, and Caveat. Use only the evidence packet."
        ),
    }


def analyze(result_path: Path, mapping_path: Path | None = DEFAULT_MAPPING_PATH) -> dict[str, Any]:
    result = load_json(result_path)
    mapping = load_json(mapping_path) if mapping_path and mapping_path.exists() else None
    tracks = get_tracks(result)
    n_timesteps = len(next(iter(tracks.values())))
    segments = get_segments(result, n_timesteps)

    normalized_tracks = {m: normalize(values) for m, values in tracks.items()}
    overall = np.mean([normalized_tracks[m] for m in MODALITIES], axis=0)

    hook_indices = window_indices(segments, 0.0, 3.0) or list(range(min(3, n_timesteps)))
    mid_indices = window_indices(segments, 3.0, 8.0)
    close_indices = window_indices(segments, max(0.0, segments[-1]["end"] - 3.0), segments[-1]["end"] + 1e-6)

    windows = {
        "hook": summarize_window("0-3s hook", hook_indices, normalized_tracks, overall),
        "middle": summarize_window("3-8s middle", mid_indices, normalized_tracks, overall),
        "close": summarize_window("last 3s close", close_indices, normalized_tracks, overall),
    }
    dips = find_dips(overall, normalized_tracks, segments)
    balance = modality_balance(tracks)
    cta = cta_window(overall, normalized_tracks, segments)
    moments = ranked_moments(overall, normalized_tracks, segments)
    movers = parcel_movers(result, mapping)
    cards = feature_cards(windows, dips, cta, balance, overall)
    evidence = evidence_summary(windows, dips, cta, balance, moments, overall)

    return {
        "source": str(result_path),
        "schema_version": 2,
        "n_timesteps": n_timesteps,
        "segments": segments,
        "raw_track_stats": {
            m: {
                "min": round(float(values.min()), 6),
                "max": round(float(values.max()), 6),
                "mean": round(float(values.mean()), 6),
            }
            for m, values in tracks.items()
        },
        "normalized_tracks": {
            m: [round(float(v), 1) for v in normalized_tracks[m]]
            for m in MODALITIES
        },
        "overall": [round(float(v), 1) for v in overall],
        "windows": windows,
        "ranked_moments": moments,
        "dips": dips,
        "cta_window": cta,
        "modality_balance": balance,
        "parcel_movers": movers,
        "event_context": event_context(result),
        "feature_cards": cards,
        "evidence_summary": evidence,
        "creator_insights": creator_insights(windows, dips, balance, cta, overall),
        "llm_context": llm_context(result_path, windows, dips, cta, balance, moments, cards, movers, result),
        "notes": [
            "Scores are normalized within this clip and should be read as relative timing signals, not universal retention percentages.",
            "This analysis is deterministic and does not use an LLM. Feed llm_context into an LLM to generate polished human-facing coaching.",
        ],
    }


def default_output_path(result_path: Path) -> Path:
    return result_path.with_name(f"{result_path.stem}_insights.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a saved Resonate inference JSON.")
    parser.add_argument("result_json", type=Path, help="Path to saved inference JSON.")
    parser.add_argument(
        "--mapping",
        type=Path,
        default=DEFAULT_MAPPING_PATH,
        help="Path to Schaefer modality mapping JSON.",
    )
    parser.add_argument("--output", type=Path, help="Output insights JSON path.")
    args = parser.parse_args()

    insights = analyze(args.result_json, args.mapping)
    output = args.output or default_output_path(args.result_json)
    with output.open("w") as f:
        json.dump(insights, f, indent=2)

    print(f"wrote {output}")
    print("creator insights:")
    for item in insights["creator_insights"]:
        print(f"- {item['title']}: {item['detail']}")


if __name__ == "__main__":
    main()
