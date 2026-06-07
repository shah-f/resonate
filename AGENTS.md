# AGENTS.md

Guidance for coding agents and humans working in this repo.

## Project Context

This repo is the working backend/planning workspace for **Resonate**, a hackathon prototype that analyzes short-form videos using Meta Tribe v2 predicted brain responses. The full product scope, feature priorities, and build order live in `PLAN.md`.

Before making product or architecture decisions, read:

1. `PLAN.md` - primary scope and feature plan.
2. `resonate_tribe_modal.py` - current backend/Modal implementation.
3. `PROGRESS.md` - concise critical handoff notes.

Use the agent-specific docs only when relevant:

- `resonate_atlas_agent.md` - Schaefer-200 atlas verification and modality grouping.
- `resonate_blue_agent.md` - reference corpus and Blueprint generation.
- `frontendAgents/resonate_frontend_agents.md` - frontend build plan.
- `frontendAgents/resonate_brain_visualization_agent.md` - 200-parcel brain visualization plan.

## Current Shape of the Repo

- `resonate_tribe_modal.py` is the main implementation file.
- `debug_text.py` is a separate Modal debug helper for neuralset/Hugging Face cache issues.
- `modal_test/` contains local validation and deployed test scripts.
- `test_clips/` contains sample input videos.
- `results/` contains generated inference artifacts.
- `reference_videos/` is intended for curated reference corpus videos and is currently mostly empty.

This directory is not currently a git repository. Be extra careful with cleanup and destructive actions because there is no local git safety net unless one is added later.

## Working Rules

- Do not delete, move, or overwrite files unless the human explicitly asks or approves a cleanup plan.
- Treat `results/`, `test_clips/`, and `reference_videos/` as data/artifact directories. Ask before removing large or generated files unless the task clearly requires it.
- Prefer small, direct changes that preserve the hackathon prototype's ability to run.
- Keep `resonate_tribe_modal.py` as the source of truth for the active Modal app unless the repo is intentionally reorganized.
- Avoid broad refactors during time-sensitive hackathon work.
- Keep docs accurate when code moves or behavior changes.

## Modal / ML Notes

- The active Modal app name is `resonate`.
- The active function is `run_tribe`.
- The Modal Volume is `tribe-model-cache`.
- The implementation uses a Hugging Face secret named `huggingface-token`.
- Tribe v2 produces fsaverage5 surface predictions with 20,484 vertices, split as 10,242 left hemisphere vertices and 10,242 right hemisphere vertices.
- Atlas mapping uses Schaefer-200 surface annotation files, not a volumetric atlas.
- Current modality grouping is keyword-based:
  - visual: `Vis`
  - audio: `SomMot`
  - language: `Default_Temp`, `Default_PFC`, `Cont_Temp`, `Cont_PFCl`
- `resonate_atlas_agent.md` says the atlas grouping should be verified before running the Blue Agent reference corpus scoring.

## Testing / Validation

Useful scripts:

- `modal_test/test_atlas_local.py` - validates Schaefer fsaverage5 atlas mapping locally without GPU cost.
- `modal_test/test_inference.py` - runs deployed `resonate/run_tribe` on any local video path and prints a summary.
- `modal_test/test_final.py` - calls deployed `resonate/run_tribe` on `test_clips/finance_test_clip.mp4` and saves outputs under `results/`.
- `modal_test/hello.py` - Modal smoke test.

Running Modal or downloading model assets may require network access, credentials, and cost-bearing GPU time. Confirm intent before running expensive remote inference. Inference scripts should check for existing `results/<clip_name>.json` or `results/<clip_name>.npz` artifacts before calling Modal.

## Progress Logging

Keep `PROGRESS.md` concise. Add only critical context future agents need to avoid mistakes or understand current state.

Good `PROGRESS.md` entries include:

- Current blockers or decisions.
- Commands/scripts whose behavior changed.
- Data/artifacts that must be preserved.
- Validation that affects future work.

Use `LOGS.md` for detailed debugging notes, exploratory analysis, command output summaries, and low-stakes task history. Small documentation-only tasks usually do not need a `PROGRESS.md` entry unless they change how agents should work.
