# Logs

Detailed notes, debugging records, and exploratory analysis. Keep `PROGRESS.md` limited to critical handoff context.

## 2026-06-07 - Repo Documentation

Added:

- `AGENTS.md` with project context, working rules, Modal/ML notes, validation scripts, and logging expectations.
- `README.md` with project overview, file map, backend flow, validation commands, and operational notes.
- `PROGRESS.md` as a concise handoff log.

Notes:

- `/Users/foramshah/brain` is not currently a git repository.
- The active backend appears to be `resonate_tribe_modal.py`, with `run_tribe` deployed under Modal app `resonate`.
- `PLAN.md` remains the source of truth for product scope, hackathon priorities, and build sequence.

## 2026-06-07 - Split Progress From Detailed Logs

Changed:

- Trimmed `PROGRESS.md` down to critical handoff context.
- Added this `LOGS.md` file for detailed debugging notes, exploratory analysis, and lower-stakes task history.
- Updated `AGENTS.md` and `README.md` so future agents know which file to use.

Guideline:

- Put durable, mistake-preventing context in `PROGRESS.md`.
- Put detailed results, command notes, and debugging history in `LOGS.md`.

## 2026-06-07 - Atlas Agent Audit Task Added

Updated `resonate_atlas_agent.md` to make the Schaefer modality-grouping audit explicit.

Reason:

- The surface Schaefer-200 plumbing already exists, but `MODALITY_KEYWORDS` are provisional until audited.
- The audit should happen before Blue Agent scores reference videos.

Added requirements:

- Report parcel counts and example parcel names per modality.
- Check unassigned network/region labels.
- Explicitly validate `SomMot` as the audio proxy.
- Explicitly validate whether the language grouping is too broad/narrow.
- Recommend saving `results/schaefer200_modality_mapping.json` so existing parcel arrays can be interpreted without rerunning Tribe.

## 2026-06-07 - Atlas Agent Audit Run

Ran the Atlas Agent audit locally. No Modal calls, no Tribe inference, and no video clips were processed.

Commands/results:

- `python3 modal_test/test_atlas_local.py`
- Local sanity check passed:
  - left hemisphere labels: 10,242 vertices
  - right hemisphere labels: 10,242 vertices
  - total surface vertices: 20,484
  - parcel names: 200
  - synthetic parcel output shape: 19 x 200
  - non-zero parcels: 200/200

Generated:

- `results/schaefer200_modality_mapping.json`

Audit counts:

- visual: 29 parcels
- audio: 35 parcels
- language: 45 parcels
- unassigned: 91 parcels

Example parcel names:

- visual:
  - `7Networks_LH_Vis_1`
  - `7Networks_LH_Vis_2`
  - `7Networks_LH_Vis_3`
- audio:
  - `7Networks_LH_SomMot_1`
  - `7Networks_LH_SomMot_2`
  - `7Networks_LH_SomMot_3`
- language:
  - `7Networks_LH_Cont_Temp_1`
  - `7Networks_LH_Cont_PFCl_1`
  - `7Networks_LH_Cont_PFCl_2`

Unassigned network/region labels:

- `Cont_Cing`
- `Cont_OFC`
- `Cont_PFCmp`
- `Cont_PFCv`
- `Cont_Par`
- `Cont_pCun`
- `Default_PHC`
- `Default_Par`
- `Default_pCunPCC`
- `DorsAttn_FEF`
- `DorsAttn_Post`
- `DorsAttn_PrCv`
- `Limbic_OFC`
- `Limbic_TempPole`
- `SalVentAttn_FrOperIns`
- `SalVentAttn_Med`
- `SalVentAttn_PFCl`
- `SalVentAttn_ParOper`
- `SalVentAttn_PrC`
- `SalVentAttn_TempOccPar`

Decision:

- No `MODALITY_KEYWORDS` changes were made.
- `SomMot` is acceptable as an audio proxy for this hackathon/demo because Schaefer-7 has no separate auditory network and auditory areas are folded into somatomotor at this atlas/network granularity.
- Language grouping is acceptable as a broad language/meaning proxy, but product copy should not claim exact Broca/Wernicke or named-region precision from this grouping alone.

## 2026-06-07 - Backend Full Signal Capture Added Locally

Updated local backend capture so future paid Modal runs preserve more useful data.

Files changed:

- `resonate_tribe_modal.py`
- `modal_test/test_final.py`
- `modal_test/test_inference.py`
- `PLAN.md`
- `PROGRESS.md`
- `LOGS.md`

Added to future `run_tribe()` responses:

- `events`: JSON-safe records/columns/shape from `model.get_events_dataframe(...)`
- richer `segments`: type, repr, start/end/duration when parseable
- `segments_parsed`: simple start/end list for player/timeline alignment
- `metadata`: filename, video size, run timestamps, model/cache paths, atlas name, modality keywords, `capture_schema_version: 2`

Updated saving in `modal_test/test_final.py`:

- JSON still stores the full result.
- NPZ now also stores:
  - `segments_parsed`
  - `event_records`
  - `event_columns`
  - `parcel_names`
  - `modality_indices`
  - `metadata`

Why this helps features:

- Engagement Autopsy can align dips with extracted event rows and exact segment timing.
- Modality Balance can explain spikes using saved event context.
- CTA Window Finder can map recommended moments to parsed start/end times instead of bare indices.
- Pacing Alert can compare scene cuts against Tribe event/segment timing.
- Old results can be re-analyzed more richly without spending Modal credits again.

Validation:

- `python3 -m py_compile resonate_tribe_modal.py modal_test/test_final.py modal_test/test_inference.py`
- `python3 modal_test/test_inference.py test_clips/finance_test_clip.mp4`

The finance inference script detected existing artifacts and skipped Modal. No Modal deployment or inference run was performed.

## 2026-06-07 - Modal Test Cleanup

Removed:

- `modal_test/tribe_inference.py`
- `modal_test/test_diag.py`

Rationale:

- `modal_test/tribe_inference.py` defined an older `resonate-tribe` app and simpler `run_tribe` implementation superseded by `resonate_tribe_modal.py`.
- `modal_test/test_diag.py` used a video path under `~/Downloads` and was superseded by retained scripts.

Kept:

- `modal_test/hello.py` as a simple Modal smoke test.
- `modal_test/test_atlas_local.py` for local atlas validation without GPU cost.
- `modal_test/test_final.py` for the checked-in finance test clip and persisted JSON/NPZ outputs.
- `modal_test/test_inference.py` for ad hoc future inference on an explicit local video path.

Also updated references to frontend agent docs under `frontendAgents/`.

## 2026-06-07 - Generic Inference Script Correction

`modal_test/test_inference.py` was restored as a generic helper after the user pointed out the future-inference workflow is useful.

Follow-up correction:

- Removed defaulting to `test_clips/finance_test_clip.mp4`.
- The script now requires a video path argument.
- If no argument is provided, argparse shows usage and no inference runs.

Validation:

- `python3 -m py_compile modal_test/test_inference.py`
- `python3 modal_test/test_inference.py --help`

## 2026-06-07 - Modal Credit Guard

Added local artifact guards before Modal calls in:

- `modal_test/test_inference.py`
- `modal_test/test_final.py`

Behavior:

- Check `results/<video_stem>.json` and `results/<video_stem>.npz`.
- If either exists, print the existing artifact path(s) and exit before importing/calling Modal.

Validation:

- `python3 -m py_compile modal_test/test_inference.py modal_test/test_final.py`
- `python3 modal_test/test_inference.py test_clips/finance_test_clip.mp4`
- `python3 modal_test/test_final.py`

Both finance checks detected existing artifacts and skipped Modal. No remote Modal inference was run.

## 2026-06-07 - First Finance Clip Data Analysis

Analyzed saved artifacts:

- `results/finance_test_clip.json`
- `results/finance_test_clip.npz`
- `test_clips/finance_test_clip.mp4`

Confirmed:

- Saved inference shape: 11 timesteps x 20,484 raw vertices.
- Saved parcel matrix: 11 timesteps x 200 parcels.
- Visual/audio/language modality tracks are present.
- Clip metadata: 10.5 seconds, vertical 608x1080, 30fps, with audio.
- No Modal calls were run.

Core data pattern:

| Window | Overall Signal | Visual | Audio | Language |
|---|---:|---:|---:|---:|
| 0-2s hook | 14/100 | 15 | 25 | 3 |
| 3-7s middle | 17/100 | 21 | 4 | 25 |
| 8-10s close | 66/100 | 67 | 56 | 74 |

Main insight:

- Combined normalized activation is weakest around second 2, remains low through the middle, then spikes sharply at seconds 9-10.
- Visual and audio both rebound late, while language rises steadily across the clip.
- Representative frames suggest the role switch and tax-bracket explanation arrive late, matching the late activation spike.

Caveat:

- The first saved result does not include `parcel_names` or `modality_indices`, so it supports modality/timing insights but not named-region brain labels.

Report saved:

- `results/finance_test_clip_analysis.md`
