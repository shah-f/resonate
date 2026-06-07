"""Convert a saved Resonate inference result into product-ready insights.

This is deterministic analysis code. It does not call Modal or an LLM.

Usage:
    python3 analysis/resonate_analysis.py results/finance_test_clip.json --video test_clips/finance_test_clip.mp4
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
    idx = int(overall.argmax())
    segment = segments[idx]
    return {
        "timestep": idx,
        "start": round(float(segment["start"]), 3),
        "end": round(float(segment["end"]), 3),
        "overall": round(float(overall[idx]), 1),
        "modalities": {m: round(float(normalized_tracks[m][idx]), 1) for m in MODALITIES},
        "note": "Best local moment for payoff/CTA based on combined normalized activation.",
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


def detect_scene_intervals(video_path: Path, threshold: float = 27.0) -> dict[str, Any]:
    """Detect scene intervals with PySceneDetect when it is installed."""
    if not video_path.exists():
        return {
            "available": False,
            "reason": f"Video not found: {video_path}",
            "video_path": str(video_path),
            "scene_intervals": [],
            "scene_cuts": [],
        }

    try:
        from scenedetect import SceneManager, open_video
        from scenedetect.detectors import ContentDetector
    except ImportError:
        return {
            "available": False,
            "reason": "PySceneDetect is not installed. Install the 'scenedetect' package to enable pacing alerts.",
            "video_path": str(video_path),
            "scene_intervals": [],
            "scene_cuts": [],
        }

    video = open_video(str(video_path))
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()

    intervals = []
    for start, end in scene_list:
        start_s = float(start.seconds)
        end_s = float(end.seconds)
        intervals.append(
            {
                "start": round(start_s, 3),
                "end": round(end_s, 3),
                "duration": round(max(0.0, end_s - start_s), 3),
            }
        )

    if not intervals and video.duration is not None:
        duration = float(video.duration.seconds)
        intervals = [{"start": 0.0, "end": round(duration, 3), "duration": round(duration, 3)}]

    return {
        "available": True,
        "reason": None,
        "video_path": str(video_path),
        "threshold": threshold,
        "scene_intervals": intervals,
        "scene_cuts": [scene["start"] for scene in intervals[1:]],
    }


def pacing_alert(
    video_path: Path | None,
    segments: list[dict[str, float]],
    overall: np.ndarray,
    normalized_tracks: dict[str, np.ndarray],
    dips: list[dict[str, Any]],
    hold_threshold_seconds: float = 2.5,
) -> dict[str, Any]:
    if video_path is None:
        return {
            "available": False,
            "reason": "No video path was provided. Pass --video to enable scene-cut pacing analysis.",
            "scene_cuts": [],
            "scene_intervals": [],
            "long_hold_warnings": [],
        }

    scene_data = detect_scene_intervals(video_path)
    if not scene_data["available"]:
        return {
            **scene_data,
            "hold_threshold_seconds": hold_threshold_seconds,
            "long_hold_warnings": [],
        }

    warnings = []
    centers = np.asarray([(s["start"] + s["end"]) / 2.0 for s in segments], dtype=float)

    for scene_index, scene in enumerate(scene_data["scene_intervals"]):
        indices = [
            int(i)
            for i, center in enumerate(centers)
            if scene["start"] <= center < scene["end"]
        ]
        if len(indices) < 2 or scene["duration"] < hold_threshold_seconds:
            continue

        first_idx = indices[0]
        last_idx = indices[-1]
        overall_delta = float(overall[last_idx] - overall[first_idx])
        dips_inside = [
            dip
            for dip in dips
            if scene["start"] <= float(dip["start"]) < scene["end"]
        ]
        if overall_delta > -8.0 and not dips_inside:
            continue

        modality_deltas = {
            m: round(float(normalized_tracks[m][last_idx] - normalized_tracks[m][first_idx]), 1)
            for m in MODALITIES
        }
        lead_modality = min(modality_deltas, key=modality_deltas.get)
        warnings.append(
            {
                "scene_index": scene_index,
                "start": scene["start"],
                "end": scene["end"],
                "duration": scene["duration"],
                "timesteps": indices,
                "overall_start": round(float(overall[first_idx]), 1),
                "overall_end": round(float(overall[last_idx]), 1),
                "overall_delta": round(overall_delta, 1),
                "lead_modality": lead_modality,
                "modality_deltas": modality_deltas,
                "aligned_dips": dips_inside,
                "suggested_fix": (
                    f"Add a visual change, cutaway, caption contrast, or delivery shift before {scene['end']:.1f}s."
                ),
            }
        )

    return {
        **scene_data,
        "hold_threshold_seconds": hold_threshold_seconds,
        "long_hold_warnings": warnings,
        "summary": (
            f"{len(warnings)} long hold(s) align with a predicted engagement drop."
            if warnings
            else "No long scene holds aligned with predicted engagement drops."
        ),
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
    pacing: dict[str, Any],
) -> dict[str, Any]:
    hook = windows["hook"]
    close = windows["close"]
    payoff_delta = None
    if hook["overall"] is not None and close["overall"] is not None:
        payoff_delta = round(float(close["overall"] - hook["overall"]), 1)

    return {
        "main_story": (
            "The strongest combined activation arrives near the end, while the hook is weak."
            if payoff_delta is not None and payoff_delta >= 25
            else "The clip has uneven activation across time."
        ),
        "payoff_delta_close_minus_hook": payoff_delta,
        "first_major_dip": dips[0] if dips else None,
        "strongest_moment": moments["strongest"][0] if moments["strongest"] else None,
        "weakest_moment": moments["weakest"][0] if moments["weakest"] else None,
        "cta_window": cta,
        "modality_balance": balance,
        "pacing_alert": {
            "available": pacing.get("available"),
            "summary": pacing.get("summary") or pacing.get("reason"),
            "first_warning": (pacing.get("long_hold_warnings") or [None])[0],
        },
    }


def feature_cards(
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    cta: dict[str, Any],
    balance: dict[str, Any],
    pacing: dict[str, Any],
) -> dict[str, Any]:
    first_dip = dips[0] if dips else None
    hook = windows["hook"]
    close = windows["close"]
    payoff_delta = (
        round(float(close["overall"] - hook["overall"]), 1)
        if hook["overall"] is not None and close["overall"] is not None
        else None
    )
    first_pacing_warning = (pacing.get("long_hold_warnings") or [None])[0]

    return {
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
            "headline": (
                "The payoff appears to land late."
                if payoff_delta is not None and payoff_delta >= 25
                else "The payoff timing is not clearly late from this run."
            ),
            "evidence": {
                "hook_overall": hook["overall"],
                "close_overall": close["overall"],
                "close_minus_hook": payoff_delta,
            },
            "suggested_fix": "Move the strongest idea, reveal, or contrast into the first 2-3 seconds.",
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
            "headline": f"Best local payoff/CTA moment is around {cta['start']:.1f}-{cta['end']:.1f}s.",
            "evidence": cta,
            "suggested_fix": "Use this timing for payoff placement, or move this moment earlier if it lands too late for short-form retention.",
        },
        "pacing_alert": {
            "headline": (
                f"Long hold from {first_pacing_warning['start']:.1f}-{first_pacing_warning['end']:.1f}s lines up with a signal drop."
                if first_pacing_warning
                else pacing.get("summary") or "Pacing analysis unavailable."
            ),
            "evidence": first_pacing_warning or {
                "available": pacing.get("available"),
                "reason": pacing.get("reason"),
                "scene_cuts": pacing.get("scene_cuts", []),
            },
            "suggested_fix": (
                first_pacing_warning["suggested_fix"]
                if first_pacing_warning
                else "Run scene detection with the source video to add pacing markers."
            ),
        },
    }


def creator_insights(
    windows: dict[str, Any],
    dips: list[dict[str, Any]],
    balance: dict[str, Any],
    cta: dict[str, Any],
) -> list[dict[str, str]]:
    insights = []

    hook = windows["hook"]
    close = windows["close"]
    if hook["overall"] is not None and close["overall"] is not None:
        if close["overall"] - hook["overall"] >= 25:
            insights.append(
                {
                    "title": "The payoff arrives late",
                    "detail": (
                        f"The close scores {close['overall']}/100 while the hook scores "
                        f"{hook['overall']}/100. Move the strongest idea earlier."
                    ),
                }
            )

    if dips:
        first = dips[0]
        insights.append(
            {
                "title": f"Attention dip around {first['start']:.1f}s",
                "detail": (
                    f"Overall signal drops {abs(first['overall_delta'])}/100, led by "
                    f"{first['lead_modality']}."
                ),
            }
        )

    insights.append(
        {
            "title": "Modality balance",
            "detail": balance["verdict"],
        }
    )
    insights.append(
        {
            "title": "Best payoff window",
            "detail": f"Strongest combined moment is around {cta['start']:.1f}-{cta['end']:.1f}s.",
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
    pacing: dict[str, Any],
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
        "pacing_alert": pacing,
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
            "For pacing, only mention scene cuts or held shots when pacing_alert.available is true.",
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


def analyze(
    result_path: Path,
    mapping_path: Path | None = DEFAULT_MAPPING_PATH,
    video_path: Path | None = None,
) -> dict[str, Any]:
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
    pacing = pacing_alert(video_path, segments, overall, normalized_tracks, dips)
    movers = parcel_movers(result, mapping)
    cards = feature_cards(windows, dips, cta, balance, pacing)
    evidence = evidence_summary(windows, dips, cta, balance, moments, pacing)

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
        "pacing_alert": pacing,
        "parcel_movers": movers,
        "event_context": event_context(result),
        "feature_cards": cards,
        "evidence_summary": evidence,
        "creator_insights": creator_insights(windows, dips, balance, cta),
        "llm_context": llm_context(result_path, windows, dips, cta, balance, moments, cards, movers, pacing, result),
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
    parser.add_argument(
        "--video",
        type=Path,
        help="Source video path for optional PySceneDetect pacing analysis.",
    )
    parser.add_argument("--output", type=Path, help="Output insights JSON path.")
    args = parser.parse_args()

    insights = analyze(args.result_json, args.mapping, args.video)
    output = args.output or default_output_path(args.result_json)
    with output.open("w") as f:
        json.dump(insights, f, indent=2)

    print(f"wrote {output}")
    print("creator insights:")
    for item in insights["creator_insights"]:
        print(f"- {item['title']}: {item['detail']}")


if __name__ == "__main__":
    main()
