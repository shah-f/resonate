# Resonate Brain Backend Workspace

Resonate is a hackathon prototype for analyzing short-form videos with predicted brain-response signals. A user uploads a video, the backend runs Meta Tribe v2 to predict cortical activation over time, maps raw fsaverage5 surface vertices into Schaefer-200 brain atlas parcels, and summarizes the result into visual, audio, and language modality tracks.

The product plan is in `PLAN.md`. Treat that file as the source of truth for scope, demo priorities, and feature ordering.

## What Is Here

- `resonate_tribe_modal.py` - active Modal backend for Tribe v2 inference and Schaefer-200 atlas mapping.
- `debug_text.py` - standalone debug helper for neuralset/Hugging Face cache inspection.
- `modal_test/` - local atlas validation, Modal smoke test, and deployed inference test script.
- `test_clips/` - sample video inputs.
- `results/` - generated inference outputs from test runs.
- `reference_videos/` - intended home for curated reference videos.
- `resonate_*_agent.md` - task briefs for specialized build agents.
- `AGENTS.md` - instructions for future coding agents.
- `PROGRESS.md` - concise critical handoff notes.
- `LOGS.md` - detailed debug notes and exploratory records.

## Core Backend Flow

1. Build a Modal image with Tribe v2 and supporting dependencies.
2. Download/cache Tribe v2 and LLaMA weights using the configured Hugging Face token.
3. Accept uploaded video bytes in `run_tribe`.
4. Run Tribe v2 inference to produce timestep-by-vertex predictions.
5. Load Schaefer-200 fsaverage5 surface labels.
6. Average vertex predictions into 200 parcel scores per timestep.
7. Group parcels into visual, audio, and language modality tracks.
8. Return raw predictions, segments, parcel scores, parcel names, modality tracks, and modality indices.

## Important Files

Read these first when getting oriented:

- `PLAN.md` - project goals, hackathon build order, and architecture.
- `AGENTS.md` - repo-specific working instructions.
- `PROGRESS.md` - critical current context and handoff notes.
- `LOGS.md` - detailed history, debugging notes, and analysis records.
- `resonate_tribe_modal.py` - current implementation.

Specialized docs:

- `resonate_atlas_agent.md` - verify/refine atlas modality groupings.
- `resonate_blue_agent.md` - create reference corpus and Blueprint files.
- `frontendAgents/resonate_frontend_agents.md` - Next.js frontend plan.
- `frontendAgents/resonate_brain_visualization_agent.md` - frontend brain visualization plan.

## Validation

Local atlas validation:

```bash
python modal_test/test_atlas_local.py
```

Modal smoke test:

```bash
modal run modal_test/hello.py
```

Run deployed inference on the included test clip:

```bash
modal run modal_test/test_final.py
```

The inference script writes generated output under `results/`.

Run deployed inference on an arbitrary local clip and print a summary. A video path is required:

```bash
python3 modal_test/test_inference.py path/to/video.mp4
```

Both inference scripts first check `results/` for an existing `<video_stem>.json` or `<video_stem>.npz` artifact and skip the Modal call if one exists.

## Operational Notes

- This workspace is a git repo connected to `https://github.com/shah-f/resonate.git`.
- Modal inference requires configured Modal auth and the `huggingface-token` secret.
- Remote inference may incur GPU time and depends on large model downloads/caches.
- `results/` and `__pycache__/` are generated artifacts.
- `test_clips/` and `reference_videos/` are data directories; do not remove their contents without confirming.

## Next Likely Work

Per `PLAN.md`, the critical backend sequence is:

1. Verify Schaefer-200 modality groupings with the Atlas Agent instructions.
2. Score curated reference videos with the Blue Agent instructions.
3. Preserve generated Blueprint artifacts for frontend/API use.
4. Wire the frontend/API layer around the Modal response shape.
