import json, os
from pathlib import Path

import numpy as np

path = "/Users/foramshah/brain/test_clips/finance_test_clip.mp4"
clip_name = os.path.splitext(os.path.basename(path))[0]
out_dir = "/Users/foramshah/brain/results"
os.makedirs(out_dir, exist_ok=True)
json_path = os.path.join(out_dir, f"{clip_name}.json")
npz_path = os.path.join(out_dir, f"{clip_name}.npz")

existing_paths = [p for p in (Path(json_path), Path(npz_path)) if p.exists()]
if existing_paths:
    print("Inference already exists for this video. Skipping Modal run.")
    print("Existing artifact(s):")
    for existing_path in existing_paths:
        print(f"  {existing_path}")
    raise SystemExit(0)

import modal

run_tribe = modal.Function.from_name("resonate", "run_tribe")

video_bytes = open(path, "rb").read()
print(f"Video: {path} ({len(video_bytes)/1024/1024:.1f} MB) — sending to Modal...")

result = run_tribe.remote(video_bytes, "finance_test_clip.mp4")

# --- PERSIST EVERYTHING the model returned, so we never lose a run again ---
with open(json_path, "w") as f:
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
print(f"💾 saved full data → {json_path}")
print(f"💾 saved arrays   → {npz_path}")

print("\n=== RESULT ===")
print("keys:", list(result.keys()))
print("shape:", result["shape"])
print("segments len:", len(result["segments"]))
if "events" in result:
    print("events:", result["events"].get("shape"), "columns:", result["events"].get("columns", [])[:8])
if "modality" in result:
    print("✅ atlas mapping SUCCEEDED")
    print("parcels:", len(result["parcels"]), "x", len(result["parcels"][0]))
    for m, v in result["modality"].items():
        n = len(v)
        mn = min(v); mx = max(v); avg = sum(v) / n
        print(f"  {m:9s}: len={n} min={mn:.4f} max={mx:.4f} mean={avg:.4f}")
else:
    print("❌ modality NOT present — atlas mapping skipped (see [diag] logs above)")
