# Progress

Critical handoff notes for humans and coding agents. Keep this file concise.

For detailed debugging notes, command outcomes, and exploratory analysis, use `LOGS.md`. For product scope and priorities, read `PLAN.md`.

## Current Critical Context

- This workspace is a git repository connected to `https://github.com/shah-f/resonate.git`.
- `PLAN.md` is the source of truth for product scope and build order.
- `resonate_tribe_modal.py` is the active Modal backend implementation.
- Active Modal app/function: `resonate` / `run_tribe`.
- Modal Volume: `tribe-model-cache`.
- Hugging Face secret expected by Modal: `huggingface-token`.
- Existing inference artifacts are under `results/`; do not delete them casually.

## Inference Safety

- `modal_test/test_inference.py` requires an explicit video path.
- `modal_test/test_final.py` targets `test_clips/finance_test_clip.mp4` and persists output.
- Both inference scripts check for existing `results/<video_stem>.json` or `results/<video_stem>.npz` before calling Modal and skip the run if artifacts already exist.
- This guard exists to conserve Modal credits.

## Saved First-Run Analysis

- First-run finance artifacts still exist:
  - `results/finance_test_clip.json`
  - `results/finance_test_clip.npz`
  - `test_clips/finance_test_clip.mp4`
- Saved human-facing analysis report:
  - `results/finance_test_clip_analysis.md`
- Important caveat: the first saved result does not include `parcel_names` or `modality_indices`, so use it for timing/modality insights, not named brain-region claims.

## Atlas Audit

- Atlas Agent audit completed locally with no Modal calls.
- Saved mapping metadata:
  - `results/schaefer200_modality_mapping.json`
- Current modality counts:
  - visual: 29 parcels
  - audio: 35 parcels
  - language: 45 parcels
- No `MODALITY_KEYWORDS` changes were made.
- Treat `SomMot` as an audio proxy for demo purposes, not as a pure auditory-only region.
- Treat language grouping as a broad language/meaning proxy, not exact Broca/Wernicke labeling.

## Cleanup Performed

- Removed superseded Modal experiment scripts:
  - `modal_test/tribe_inference.py`
  - `modal_test/test_diag.py`
- Restored `modal_test/test_inference.py` as a cleaner future-inference helper with an explicit required video path.
- Kept useful scripts:
  - `modal_test/hello.py`
  - `modal_test/test_atlas_local.py`
  - `modal_test/test_inference.py`
  - `modal_test/test_final.py`

## Documentation Added

- Added `AGENTS.md`, `README.md`, and `PROGRESS.md`.
- Added `LOGS.md` for detailed logs/debug notes.
- Frontend agent docs currently live under `frontendAgents/`.

## GitHub

- `PLAN.md` and `README.md` were pushed to `shah-f/resonate` on branch `main`.
- Only those two files are tracked in git so far; the rest of the workspace remains untracked locally.
