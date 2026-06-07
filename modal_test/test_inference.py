"""Run deployed Resonate/Tribe inference on a local video.

Usage:
    python modal_test/test_inference.py path/to/video.mp4
"""
import argparse
import os
from pathlib import Path


RESULTS_DIR = Path("/Users/foramshah/brain/results")


def existing_result_paths(video_path):
    clip_name = Path(video_path).stem
    candidates = [
        RESULTS_DIR / f"{clip_name}.json",
        RESULTS_DIR / f"{clip_name}.npz",
    ]
    return [path for path in candidates if path.exists()]


def main():
    parser = argparse.ArgumentParser(description="Run deployed Resonate inference on a video.")
    parser.add_argument(
        "video_path",
        help="Path to a local video file.",
    )
    args = parser.parse_args()

    video_path = os.path.abspath(os.path.expanduser(args.video_path))
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    existing_paths = existing_result_paths(video_path)
    if existing_paths:
        print("Inference already exists for this video. Skipping Modal run.")
        print("Existing artifact(s):")
        for path in existing_paths:
            print(f"  {path}")
        return

    import modal

    run_tribe = modal.Function.from_name("resonate", "run_tribe")

    print(f"Loading video: {video_path}")
    video_bytes = open(video_path, "rb").read()
    print(f"Video size: {len(video_bytes) / 1024 / 1024:.1f} MB")
    print("Sending to Modal...")

    result = run_tribe.remote(video_bytes, os.path.basename(video_path))

    print("Inference complete.")
    print(f"Prediction shape: {result['shape']} (timesteps x vertices)")
    if "events" in result:
        print(f"Events shape: {result['events'].get('shape')}")
    if "segments_parsed" in result:
        print(f"Parsed segments: {len(result['segments_parsed'])}")
    if "modality" in result:
        print("Modality tracks:")
        for modality in ("visual", "audio", "language"):
            print(f"  {modality}: {len(result['modality'][modality])} timesteps")
    if "parcels" in result and result["parcels"]:
        print(f"Parcels shape: {len(result['parcels'])} timesteps x {len(result['parcels'][0])} regions")


if __name__ == "__main__":
    main()
