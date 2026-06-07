"""
Validate Tribe v2 engagement predictions against actual TikTok/YouTube retention metrics.

This script:
1. Runs the mcat-prep-test-clip through Tribe v2
2. Extracts per-timestep modality activation (visual, audio, language)
3. Computes a predicted engagement curve (0-1 retention probability per second)
4. Compares predicted metrics against ground truth from tiktok_video_analytics.md

Ground truth for mcat-prep-test-clip.mov:
  - Duration: 14.42s
  - Average Watch Time: 10.0s
  - Watched Full Video: 30.75%
  - Average Retention: 70%

Success criteria:
  - Predicted avg engagement should correlate with 70% avg retention
  - Predicted engagement should drop at expected points matching viewer drop-offs
  - Predicted avg watch time should be near 10.0s
"""

import json
import os
from pathlib import Path
import numpy as np

RESULTS_DIR = Path("/Users/foramshah/brain/results")
ACTUAL_STATS = {
    "duration_sec": 14.42,
    "avg_watch_time_sec": 10.0,
    "full_video_watched_pct": 30.75,
    "avg_retention_pct": 70.0,
}

def normalize_minmax(arr):
    """Normalize array to [0, 1] range."""
    mn, mx = arr.min(), arr.max()
    if mx <= mn:
        return np.ones_like(arr)
    return (arr - mn) / (mx - mn)

def compute_retention_curve(modality_scores: dict, duration_sec: float) -> dict:
    """
    Convert per-modality activation into a predicted retention curve.
    
    Strategy: 
    - Combine visual/audio/language into overall engagement signal
    - Normalize to [0, 1] as retention probability at each timestep
    - Compute predicted watch time and full-video completion rate
    
    Returns:
      engagement: (n_timesteps,) normalized engagement per timestep
      predicted_avg_engagement: float in [0, 1]
      predicted_avg_watch_time_sec: estimated seconds user watches before dropping
      predicted_full_completion_pct: estimated % who watch entire video
    """
    # Extract modality time series
    visual = np.asarray(modality_scores.get("visual", []))
    audio = np.asarray(modality_scores.get("audio", []))
    language = np.asarray(modality_scores.get("language", []))
    
    if len(visual) == 0 or len(audio) == 0 or len(language) == 0:
        raise ValueError("Missing modality scores")
    
    n_timesteps = len(visual)
    print(f"Modality scores: visual={visual.shape}, audio={audio.shape}, language={language.shape}")
    
    # Normalize each modality independently
    visual_norm = normalize_minmax(visual)
    audio_norm = normalize_minmax(audio)
    language_norm = normalize_minmax(language)
    
    # Combine: weighted average (equal weight for now; could tune)
    engagement = 0.33 * visual_norm + 0.33 * audio_norm + 0.33 * language_norm
    
    # Overall predicted engagement (0-1)
    predicted_avg_engagement = float(np.mean(engagement))
    
    # Estimate watch time: 
    # Assume retention drops sharply when engagement falls below a threshold
    # Use a sigmoid-like decay: watch time ~ integral of engagement curve
    # Simpler heuristic: find where cumulative engagement drops below 50%
    cumsum_engagement = np.cumsum(engagement) / np.sum(engagement)
    dropoff_idx = np.argmax(cumsum_engagement >= 0.5)  # where 50% of engagement is consumed
    if dropoff_idx == 0:
        dropoff_idx = max(1, n_timesteps // 2)
    
    fps = n_timesteps / duration_sec  # frames per second (assuming uniform sampling)
    predicted_watch_time_sec = (dropoff_idx + 1) / fps
    
    # Estimate full completion: % of timesteps with engagement > 0.3 (above "noise floor")
    above_threshold = np.sum(engagement > 0.3) / n_timesteps * 100
    
    return {
        "engagement": engagement,
        "engagement_per_sec": engagement,  # for timeline visualization
        "predicted_avg_engagement": predicted_avg_engagement,
        "predicted_watch_time_sec": predicted_watch_time_sec,
        "predicted_full_completion_pct": above_threshold,
        "fps": fps,
        "n_timesteps": n_timesteps,
    }

def run_inference(video_path: str):
    """Call Modal run_tribe endpoint on video file."""
    import modal
    
    video_bytes = open(video_path, "rb").read()
    print(f"Loading video: {video_path} ({len(video_bytes)/1024/1024:.1f} MB)")
    
    run_tribe = modal.Function.from_name("resonate", "run_tribe")
    print("Calling Modal run_tribe (this may take 2-3 minutes for a long video)...")
    result = run_tribe.remote(video_bytes, Path(video_path).name)
    
    return result

def main():
    video_path = "/Users/foramshah/brain/test_clips/mcat-prep-test-clip.mov"
    clip_name = Path(video_path).stem
    
    # Check for cached results
    json_path = RESULTS_DIR / f"{clip_name}.json"
    if json_path.exists():
        print(f"Loading cached results from {json_path}")
        with open(json_path) as f:
            result = json.load(f)
    else:
        print(f"No cache; running inference via Modal (full video, ~80s)...")
        result = run_inference(video_path)
        # Save for future runs
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(result, f)
        print(f"Saved to {json_path}")
    
    # Extract modality scores
    modality = result.get("modality", {})
    if not modality:
        print("ERROR: No modality scores in result")
        return
    
    # Get actual video duration from metadata
    actual_duration = result.get("metadata", {}).get("duration_sec", ACTUAL_STATS["duration_sec"])
    
    # Compute predicted retention curve
    pred = compute_retention_curve(modality, actual_duration)
    
    print("\n" + "="*70)
    print("TRIBE PREDICTION ANALYSIS")
    print("="*70)
    print(f"\nVideo: {clip_name}")
    print(f"Duration: {actual_duration}s (actual file: 80.5s)")
    print(f"Timesteps: {pred['n_timesteps']} (fps: {pred['fps']:.1f})")
    
    print(f"\n--- ENGAGEMENT (0-1, 1=max) ---")
    print(f"Predicted avg engagement: {pred['predicted_avg_engagement']:.3f}")
    
    if ACTUAL_STATS.get('avg_retention_pct'):
        print(f"Actual avg retention %:   {ACTUAL_STATS['avg_retention_pct']/100:.3f} (70%)")
        delta_eng = abs(pred['predicted_avg_engagement'] - ACTUAL_STATS['avg_retention_pct']/100)
        print(f"Delta: {delta_eng:.3f}")
    else:
        print("(No ground truth retention data for this video)")
    
    print(f"\n--- WATCH TIME (seconds) ---")
    print(f"Predicted avg watch time: {pred['predicted_watch_time_sec']:.2f}s")
    
    if ACTUAL_STATS.get('avg_watch_time_sec'):
        print(f"Actual avg watch time:    {ACTUAL_STATS['avg_watch_time_sec']:.2f}s")
        delta_watch = abs(pred['predicted_watch_time_sec'] - ACTUAL_STATS['avg_watch_time_sec'])
        print(f"Delta: {delta_watch:.2f}s ({delta_watch/ACTUAL_STATS['avg_watch_time_sec']*100:.1f}%)")
    else:
        print("(No ground truth watch time data for this video)")
    
    print(f"\n--- FULL VIDEO COMPLETION (%) ---")
    print(f"Predicted completion:  {pred['predicted_full_completion_pct']:.2f}%")
    
    if ACTUAL_STATS.get('full_video_watched_pct'):
        print(f"Actual completion:     {ACTUAL_STATS['full_video_watched_pct']:.2f}%")
        delta_comp = abs(pred['predicted_full_completion_pct'] - ACTUAL_STATS['full_video_watched_pct'])
        print(f"Delta: {delta_comp:.2f}%")
    else:
        print("(No ground truth completion data for this video)")
    
    print("\n" + "="*70)
    
    # Score: how well do predictions match ground truth?
    score = 0
    reasons = []
    
    if ACTUAL_STATS.get('avg_retention_pct'):
        delta_eng = abs(pred['predicted_avg_engagement'] - ACTUAL_STATS['avg_retention_pct']/100)
        if delta_eng < 0.15:
            score += 40
            reasons.append(f"✓ Engagement prediction within 15% ({delta_eng:.3f})")
        else:
            reasons.append(f"✗ Engagement off by {delta_eng:.3f}")
    
    if ACTUAL_STATS.get('avg_watch_time_sec'):
        delta_watch = abs(pred['predicted_watch_time_sec'] - ACTUAL_STATS['avg_watch_time_sec'])
        if delta_watch < 1.5:
            score += 35
            reasons.append(f"✓ Watch time within 1.5s ({delta_watch:.2f}s)")
        else:
            reasons.append(f"✗ Watch time off by {delta_watch:.2f}s")
    
    if ACTUAL_STATS.get('full_video_watched_pct'):
        delta_comp = abs(pred['predicted_full_completion_pct'] - ACTUAL_STATS['full_video_watched_pct'])
        if delta_comp < 15:
            score += 25
            reasons.append(f"✓ Completion within 15% ({delta_comp:.2f}%)")
        else:
            reasons.append(f"✗ Completion off by {delta_comp:.2f}%")
    
    if score == 0 and not reasons:
        print("⚠️  NO GROUND TRUTH DATA")
        print("Video processed successfully, but no ground truth retention data available for comparison.")
        print("To add validation: collect actual viewer retention data for this MCAT clip.")
    else:
        print("VALIDATION SCORE")
        print(f"  {score}/100")
        for reason in reasons:
            print(f"  {reason}")
    
        print("\nINTERPRETATION:")
        if score >= 75:
            print("✅ STRONG CORRELATION — Tribe predictions track actual retention well!")
        elif score >= 50:
            print("🟡 MODERATE CORRELATION — directionally correct but needs tuning")
        else:
            print("❌ WEAK CORRELATION — predictions don't match ground truth; check modality grouping")
    
    return result, pred

if __name__ == "__main__":
    result, pred = main()
