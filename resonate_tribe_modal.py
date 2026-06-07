import modal
from pathlib import Path

# Modal Volume to cache model weights — prevents re-downloading on every run
volume = modal.Volume.from_name("tribe-model-cache", create_if_missing=True)

# Build the container image with Tribe v2 installed from source
# Model weights are downloaded during image build and baked in — no download at inference time
image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "ffmpeg", "libx265-dev", "libx264-dev")
    .run_commands(
        "git clone https://github.com/facebookresearch/tribev2 /tribev2",
        "pip install 'exca==0.5.25'",  # pin before tribev2 install — exca 0.5.26 breaks neuralset
        "cd /tribev2 && pip install -e .[plotting]",  # plotting gives us nilearn for atlas
        # tribev2 leaves transformers UNPINNED, so pip pulls transformers 5.x which
        # needs torch>=2.7 (torch.float8_e8m0fnu) — but tribev2 caps torch<2.7.
        # Pin to 4.53.x: the narrow window that has V-JEPA2 (added 4.53.0) + Wav2Vec2-BERT
        # + Llama, yet still predates the torch.float8_e8m0fnu reference (lands ~4.54, needs
        # torch>=2.7 which tribev2 forbids). accelerate is required by device_map="auto".
        "pip install 'transformers==4.53.3' 'accelerate>=0.26.0'",
    )
    # HF_HOME points the HuggingFace cache at a baked-in path so Tribe's
    # internal LLaMA load (via neuralset) finds weights instead of re-downloading.
    .env({"HF_HOME": "/model_cache/hf"})
    .run_commands(
        # Pre-download Tribe v2 + LLaMA weights into the image during build.
        # Secret is passed here (not via .env) so HF_TOKEN is available for gated repos.
        "python3 -c \""
        "from huggingface_hub import login, snapshot_download; import os; "
        "login(token=os.environ['HF_TOKEN']); "
        "snapshot_download('facebook/tribev2', local_dir='/model_cache/tribev2'); "
        "snapshot_download('meta-llama/Llama-3.2-3B'); "  # into HF_HOME cache, where neuralset looks
        "\"",
        secrets=[modal.Secret.from_name("huggingface-token")],
    )
)

app = modal.App("resonate", image=image)

# Schaefer-200 SURFACE parcellation (fsaverage5) — annot files from the CBIG/Yeo lab.
# Tribe v2 outputs per-vertex activation on the fsaverage5 surface (20484 verts =
# 10242 per hemisphere), NOT a volumetric atlas — so we need the SURFACE labels.
SCHAEFER_FS5_BASE = (
    "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master/stable_projects/"
    "brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/FreeSurfer5.3/"
    "fsaverage5/label"
)
SCHAEFER_FS5_FILES = {
    "lh": "lh.Schaefer2018_200Parcels_7Networks_order.annot",
    "rh": "rh.Schaefer2018_200Parcels_7Networks_order.annot",
}

# Per-modality grouping by Schaefer 7-network label substrings.
# Visual = Vis network; Audio ≈ SomMot (Schaefer folds auditory cortex into
# somatomotor); Language ≈ Default/Control temporal + lateral-PFC parcels.
# NOTE: these are sensible defaults — the Atlas Agent refines them from real names.
MODALITY_KEYWORDS = {
    "visual":   ["Vis"],
    "audio":    ["SomMot"],
    "language": ["Default_Temp", "Default_PFC", "Cont_Temp", "Cont_PFCl"],
}


def _load_schaefer_fs5(cache_dir: str = "/cache/schaefer_fs5"):
    """Download + read the fsaverage5 Schaefer-200 annot files. Returns
    (lh_labels, rh_labels, parcel_names) where labels are per-vertex parcel
    ids (0 = medial wall, 1..100 per hemisphere) and parcel_names has length 200."""
    import os, urllib.request
    import numpy as np
    import nibabel as nib

    os.makedirs(cache_dir, exist_ok=True)
    hemi_labels = {}
    hemi_names = {}
    for hemi, fname in SCHAEFER_FS5_FILES.items():
        path = os.path.join(cache_dir, fname)
        if not os.path.exists(path):
            urllib.request.urlretrieve(f"{SCHAEFER_FS5_BASE}/{fname}", path)
        labels, _ctab, names = nib.freesurfer.io.read_annot(path)
        hemi_labels[hemi] = labels
        # names[0] is the medial-wall / background entry; parcels are names[1:]
        hemi_names[hemi] = [n.decode() if isinstance(n, bytes) else n for n in names]

    # Global parcel names: lh parcels 1..100 -> idx 0..99, rh 1..100 -> idx 100..199
    parcel_names = hemi_names["lh"][1:101] + hemi_names["rh"][1:101]
    return hemi_labels["lh"], hemi_labels["rh"], parcel_names


def apply_atlas(preds: "np.ndarray") -> dict:
    """
    Map raw Tribe v2 fsaverage5 surface predictions (n_timesteps x 20484) to:
      - 200 named Schaefer parcel scores per timestep
      - Per-modality (visual, audio, language) scores per timestep

    Vertices are assumed concatenated [left hemi (10242), right hemi (10242)].

    Returns:
      parcels:  (n_timesteps x 200)
      visual/audio/language: (n_timesteps,)
      parcel_names: list[str] of length 200 (region labels)
      modality_indices: dict[str, list[int]] (which parcels feed each modality)
    """
    import numpy as np

    n_timesteps, n_vertices = preds.shape
    per_hemi = n_vertices // 2  # 10242 for fsaverage5
    lh_lab, rh_lab, parcel_names = _load_schaefer_fs5()
    lh_pred = preds[:, :per_hemi]
    rh_pred = preds[:, per_hemi:]

    # Average surface vertices within each parcel
    parcel_scores = np.zeros((n_timesteps, 200))
    for p in range(1, 101):  # 100 parcels per hemisphere
        m = lh_lab == p
        if m.any():
            parcel_scores[:, p - 1] = lh_pred[:, m].mean(axis=1)
        m = rh_lab == p
        if m.any():
            parcel_scores[:, 100 + p - 1] = rh_pred[:, m].mean(axis=1)

    # Build per-modality parcel index lists from real parcel names
    modality_indices = {m: [] for m in MODALITY_KEYWORDS}
    for idx, name in enumerate(parcel_names):
        for modality, keywords in MODALITY_KEYWORDS.items():
            if any(kw in name for kw in keywords):
                modality_indices[modality].append(idx)

    modality_scores = {}
    for modality, indices in modality_indices.items():
        if indices:
            modality_scores[modality] = parcel_scores[:, indices].mean(axis=1)
        else:
            modality_scores[modality] = np.zeros(n_timesteps)

    return {
        "parcels": parcel_scores,
        "visual": modality_scores["visual"],
        "audio": modality_scores["audio"],
        "language": modality_scores["language"],
        "parcel_names": parcel_names,
        "modality_indices": modality_indices,
    }

@app.function(
    gpu="A10G",
    volumes={"/cache": volume},
    secrets=[modal.Secret.from_name("huggingface-token")],
    timeout=900,  # 15 min — first run downloads model weights
    memory=16384, # 16GB RAM
)
def run_tribe(video_bytes: bytes, filename: str = "video.mp4") -> dict:
    import os
    import tempfile
    import time
    import numpy as np
    from tribev2 import TribeModel

    run_started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _json_safe(value):
        """Convert common numpy/pandas objects into JSON-safe Python values."""
        import math
        import numpy as np

        if value is None or isinstance(value, (str, bool, int)):
            return value
        if isinstance(value, float):
            return value if math.isfinite(value) else None
        if isinstance(value, np.generic):
            return _json_safe(value.item())
        if isinstance(value, np.ndarray):
            return [_json_safe(v) for v in value.tolist()]
        if isinstance(value, dict):
            return {str(k): _json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_json_safe(v) for v in value]
        try:
            import pandas as pd
            if pd.isna(value):
                return None
        except Exception:
            pass
        return str(value)

    # Explicitly login to HuggingFace so gated models (LLaMA) can be downloaded
    from huggingface_hub import login
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        login(token=hf_token)

    # Write video bytes to a temp file
    with tempfile.NamedTemporaryFile(suffix=f"_{filename}", delete=False) as f:
        f.write(video_bytes)
        video_path = f.name

    # Load model from baked-in image path — no download needed
    model = TribeModel.from_pretrained(
        "/model_cache/tribev2",
        cache_folder="/cache",
    )

    # Run inference
    df = model.get_events_dataframe(video_path=video_path)
    preds, segments = model.predict(events=df)
    # preds shape: (n_timesteps, n_vertices)

    events_payload = {
        "columns": [str(c) for c in getattr(df, "columns", [])],
        "records": _json_safe(df.to_dict(orient="records")) if hasattr(df, "to_dict") else [],
        "shape": list(df.shape) if hasattr(df, "shape") else None,
    }

    os.unlink(video_path)

    # --- DIAGNOSTICS: understand the real output format before atlas mapping ---
    preds = np.asarray(preds)
    print(f"[diag] preds type={type(preds)} shape={preds.shape} dtype={preds.dtype}")
    print(f"[diag] preds min={preds.min():.4f} max={preds.max():.4f} mean={preds.mean():.4f}")
    print(f"[diag] segments type={type(segments)} n={len(segments)}")
    if len(segments):
        print(f"[diag] segment[0] type={type(segments[0])} repr={str(segments[0])[:200]}")

    # segments are neuralset objects (not importable locally) → convert to plain
    # serializable types so the result can be unpickled on the client.
    def _seg_to_plain(s):
        # Prefer numeric start/end timing if present; handle common attribute shapes.
        # Return a dict when possible, otherwise fall back to a rich repr payload.
        import re

        base = {
            "type": f"{type(s).__module__}.{type(s).__name__}",
            "repr": str(s),
        }

        # Common attribute combinations. Also handle (start, duration).
        if all(hasattr(s, a) for a in ("start", "end")):
            try:
                return {**base, "start": float(getattr(s, "start")), "end": float(getattr(s, "end"))}
            except Exception:
                pass
        if all(hasattr(s, a) for a in ("start", "duration")):
            try:
                st = float(getattr(s, "start"))
                dur = float(getattr(s, "duration"))
                return {**base, "start": st, "duration": dur, "end": st + dur}
            except Exception:
                pass
        for attrs in (("start_time", "end_time"), ("tmin", "tmax")):
            if all(hasattr(s, a) for a in attrs):
                try:
                    return {
                        **base,
                        "start": float(getattr(s, attrs[0])),
                        "end": float(getattr(s, attrs[1])),
                    }
                except Exception:
                    pass

        # Plain numeric segment (single timestamp)
        if isinstance(s, (int, float)):
            return {**base, "start": float(s), "end": float(s)}

        # Fallback: try to parse common patterns from the string repr.
        s_str = str(s)
        # Try to find start and duration
        m_start = re.search(r"start\s*=\s*[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", s_str)
        m_dur = re.search(r"duration\s*=\s*[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", s_str)
        m_end = re.search(r"end\s*=\s*[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", s_str)
        try:
            if m_start and m_dur:
                st = float(re.search(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", m_start.group(0)).group(0))
                dur = float(re.search(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", m_dur.group(0)).group(0))
                return {**base, "start": st, "duration": dur, "end": st + dur}
            if m_start and m_end:
                st = float(re.search(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", m_start.group(0)).group(0))
                ed = float(re.search(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?", m_end.group(0)).group(0))
                return {**base, "start": st, "end": ed}
        except Exception:
            pass

        # Last resort: return the original string plus type so callers can still inspect it.
        return base

    segments_plain = [_seg_to_plain(s) for s in segments]
    segments_parsed = [
        {"start": s["start"], "end": s["end"]}
        for s in segments_plain
        if isinstance(s, dict) and "start" in s and "end" in s
    ]

    # Apply Schaefer-200 atlas → per-region and per-modality scores.
    # Guarded: if atlas mapping fails, still return raw preds so we get a round-trip.
    atlas_result = None
    try:
        atlas_result = apply_atlas(preds)
    except Exception as e:
        import traceback
        print("[diag] apply_atlas FAILED (continuing with raw preds only):")
        traceback.print_exc()

    out = {
        "predictions": preds.tolist(),   # raw (n_timesteps x n_vertices)
        "segments": segments_plain,
        "segments_parsed": segments_parsed,
        "events": events_payload,
        "shape": list(preds.shape),
        "metadata": {
            "filename": filename,
            "video_size_bytes": len(video_bytes),
            "run_started_at": run_started_at,
            "run_completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tribe_model_path": "/model_cache/tribev2",
            "cache_folder": "/cache",
            "atlas": "Schaefer2018_200Parcels_7Networks_order fsaverage5 surface",
            "modality_keywords": MODALITY_KEYWORDS,
            "capture_schema_version": 2,
        },
    }
    if atlas_result is not None:
        out["parcels"] = atlas_result["parcels"].tolist()
        out["modality"] = {
            "visual":   atlas_result["visual"].tolist(),
            "audio":    atlas_result["audio"].tolist(),
            "language": atlas_result["language"].tolist(),
        }
        # Include human-readable parcel names and modality->parcel indices so
        # downstream clients and agents can reference the exact mapping used.
        out["parcel_names"] = atlas_result.get("parcel_names", [])
        # Ensure modality indices are plain lists (JSON-serializable)
        modality_indices = {}
        for k, v in atlas_result.get("modality_indices", {}).items():
            try:
                modality_indices[k] = [int(x) for x in v]
            except Exception:
                modality_indices[k] = list(v)
        out["modality_indices"] = modality_indices
    else:
        # Atlas mapping failed — still return the keys so clients can handle absence.
        out["parcel_names"] = []
        out["modality_indices"] = {m: [] for m in MODALITY_KEYWORDS}
    return out

@app.function(
    volumes={"/cache": volume},
    secrets=[modal.Secret.from_name("huggingface-token")],
    timeout=600,
)
def debug_text():
    """Inspect neuralset's text extractor source + HF cache to diagnose LLaMA load failure."""
    import os
    src_path = "/usr/local/lib/python3.11/site-packages/neuralset/extractors/text.py"
    with open(src_path) as f:
        lines = f.readlines()
    print("=== text.py lines 290-360 ===")
    for i in range(289, min(360, len(lines))):
        print(f"{i+1:4d} {lines[i]}", end="")

    print("\n=== HF_HOME ===", os.environ.get("HF_HOME"))
    print("=== HF_TOKEN set? ===", bool(os.environ.get("HF_TOKEN")))

    hf_home = os.environ.get("HF_HOME", "/root/.cache/huggingface")
    print(f"\n=== contents of {hf_home} (depth<=3) ===")
    for root, dirs, files in os.walk(hf_home):
        if root.replace(hf_home, "").count("/") <= 3:
            print(root)


@app.function(
    gpu="A10G",
    volumes={"/cache": volume},
    secrets=[modal.Secret.from_name("huggingface-token")],
    timeout=600,
)
def debug_load():
    """Reproduce neuralset's exact LLaMA load to surface the REAL (swallowed) exception."""
    import os, traceback, importlib.util
    from huggingface_hub import login
    login(token=os.environ["HF_TOKEN"])

    print("accelerate installed?:", importlib.util.find_spec("accelerate") is not None)
    try:
        import accelerate
        print("accelerate version:", accelerate.__version__)
    except Exception as e:
        print("accelerate import error:", e)

    import torch, transformers
    print("transformers:", transformers.__version__)
    from transformers import AutoModel, AutoTokenizer, AutoConfig
    print("\n--- vjepa2 config (video backbone recognized?) ---")
    try:
        AutoConfig.from_pretrained("facebook/vjepa2-vitg-fpc64-256")
        print("vjepa2 config OK")
    except Exception:
        traceback.print_exc()
    name = "meta-llama/Llama-3.2-3B"
    print("\n--- tokenizer ---")
    try:
        AutoTokenizer.from_pretrained(name, truncation_side="left")
        print("tokenizer OK")
    except Exception:
        traceback.print_exc()
    print("\n--- model (device_map=auto, fp16) ---")
    try:
        AutoModel.from_pretrained(name, device_map="auto", torch_dtype=torch.float16)
        print("model OK")
    except Exception:
        traceback.print_exc()


@app.local_entrypoint()
def dbg():
    debug_text.remote()


@app.function(timeout=120)
def debug_versions():
    import torch, transformers
    print("torch:", torch.__version__)
    print("transformers:", transformers.__version__)
    print("has float8_e8m0fnu:", hasattr(torch, "float8_e8m0fnu"))
    # show what tribev2 pinned, if anything
    import subprocess
    print(subprocess.run(["pip", "show", "tribev2", "transformers", "torch"],
                         capture_output=True, text=True).stdout)


@app.local_entrypoint()
def dbg2():
    debug_load.remote()


@app.local_entrypoint()
def dbg3():
    debug_versions.remote()


@app.local_entrypoint()
def main():
    print("Resonate — Tribe v2 inference endpoint")
    print("First run downloads model weights (~several GB) and may take 10-15 min.")
    print("Subsequent runs use cached weights from Modal Volume.")
    print("")
    print("Output per video:")
    print("  modality.visual   — visual cortex activation over time")
    print("  modality.audio    — auditory cortex activation over time")
    print("  modality.language — language region activation over time")
    print("  parcels           — all 200 Schaefer region scores over time")
