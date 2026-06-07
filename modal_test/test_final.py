import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO_PATH = PROJECT_ROOT / "test_clips" / "finance_test_clip.mp4"
RESULTS_DIR = PROJECT_ROOT / "results"


def parse_args():
    parser = argparse.ArgumentParser(description="Run the finance demo clip and persist full inference artifacts.")
    parser.add_argument(
        "--video",
        default=str(DEFAULT_VIDEO_PATH),
        help="Path to the local video file. Defaults to test_clips/finance_test_clip.mp4.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Call Modal even when results/<video_stem>.json or .npz already exists.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    video_path = Path(args.video).expanduser().resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    clip_name = video_path.stem
    RESULTS_DIR.mkdir(exist_ok=True)
    json_path = RESULTS_DIR / f"{clip_name}.json"
    npz_path = RESULTS_DIR / f"{clip_name}.npz"

    existing_paths = [path for path in (json_path, npz_path) if path.exists()]
    if existing_paths and not args.force:
        print("Inference already exists for this video. Skipping Modal run.")
        print("Existing artifact(s):")
        for existing_path in existing_paths:
            print(f"  {existing_path}")
        raise SystemExit(0)
    if existing_paths and args.force:
        print("Existing artifact(s) found, but --force was provided. Calling Modal anyway.")

    import modal
    import numpy as np

    run_tribe = modal.Function.from_name("resonate", "run_tribe")

    with video_path.open("rb") as f:
        video_bytes = f.read()
    print(f"Video: {video_path} ({len(video_bytes)/1024/1024:.1f} MB) - sending to Modal...")

    result = run_tribe.remote(video_bytes, video_path.name)

    # Persist everything the model returned, so we never lose a paid run.
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(result, f)
    np.savez_compressed(
        npz_path,
        predictions=np.asarray(result["predictions"], dtype=np.float32),
        parcels=np.asarray(result.get("parcels", []), dtype=np.float32),
        visual=np.asarray(result.get("modality", {}).get("visual", []), dtype=np.float32),
        audio=np.asarray(result.get("modality", {}).get("audio", []), dtype=np.float32),
        language=np.asarray(result.get("modality", {}).get("language", []), dtype=np.float32),
        segments=np.asarray(result.get("segments", []), dtype=object),
        segments_parsed=np.asarray(result.get("segments_parsed", []), dtype=object),
        event_records=np.asarray(result.get("events", {}).get("records", []), dtype=object),
        event_columns=np.asarray(result.get("events", {}).get("columns", []), dtype=object),
        parcel_names=np.asarray(result.get("parcel_names", []), dtype=object),
        modality_indices=np.asarray([result.get("modality_indices", {})], dtype=object),
        metadata=np.asarray([result.get("metadata", {})], dtype=object),
    )
    print(f"Saved full data -> {json_path}")
    print(f"Saved arrays    -> {npz_path}")

    print("\n=== RESULT ===")
    print("keys:", list(result.keys()))
    print("shape:", result["shape"])
    print("segments len:", len(result["segments"]))
    if "events" in result:
        print("events:", result["events"].get("shape"), "columns:", result["events"].get("columns", [])[:8])
    if "modality" in result:
        print("atlas mapping SUCCEEDED")
        print("parcels:", len(result["parcels"]), "x", len(result["parcels"][0]))
        for modality, values in result["modality"].items():
            n = len(values)
            mn = min(values)
            mx = max(values)
            avg = sum(values) / n
            print(f"  {modality:9s}: len={n} min={mn:.4f} max={mx:.4f} mean={avg:.4f}")
    else:
        print("modality NOT present - atlas mapping skipped (see [diag] logs above)")


if __name__ == "__main__":
    main()
