# Atlas Agent — Verify & Refine Schaefer-200 Modality Groupings

## What You Are
You are Atlas Agent. Your job is to verify and refine the Schaefer-200 brain-region
groupings that Resonate uses to split Tribe v2's predictions into visual / audio /
language modality tracks. The mapping logic already works (it's in
`resonate_tribe_modal.py` → `apply_atlas`). Your job is to confirm the parcel→modality
keyword groupings are neuroscientifically sound and tighten them if needed.

## Critical context — surface, NOT volume
Tribe v2 outputs **per-vertex activation on the fsaverage5 SURFACE mesh**:
`(n_timesteps, 20484)` where 20484 = 10242 vertices/hemisphere × 2.
It is **not** a volumetric image and is **not** pre-parcellated.

This means you must use the **fsaverage5 surface Schaefer-200 `.annot` files** (from the
CBIG/Yeo lab), read with `nibabel.freesurfer.io.read_annot`. **Do NOT use**
`nilearn.datasets.fetch_atlas_schaefer_2018(...)` — that returns a *volumetric* atlas
whose `.maps` is a NIfTI file path, which silently breaks surface code (it caused the
`'bool' object has no attribute 'sum'` crash we already fixed).

---

## How it currently works (already implemented & verified)

In `resonate_tribe_modal.py`:

```python
SCHAEFER_FS5_BASE = ".../FreeSurfer5.3/fsaverage5/label"
SCHAEFER_FS5_FILES = {
    "lh": "lh.Schaefer2018_200Parcels_7Networks_order.annot",
    "rh": "rh.Schaefer2018_200Parcels_7Networks_order.annot",
}

MODALITY_KEYWORDS = {
    "visual":   ["Vis"],
    "audio":    ["SomMot"],                                  # Schaefer folds auditory into SomMot
    "language": ["Default_Temp", "Default_PFC", "Cont_Temp", "Cont_PFCl"],
}
```

`_load_schaefer_fs5()` downloads the two annot files (caches them under
`/cache/schaefer_fs5`), reads per-vertex parcel ids (0 = medial wall, 1..100 per hemi),
and builds 200 global parcel names (lh 1..100 → idx 0..99, rh 1..100 → idx 100..199).

`apply_atlas(preds)` splits preds into `[lh(10242), rh(10242)]`, averages vertices within
each parcel → `(n_timesteps, 200)`, then groups parcels into visual/audio/language by
substring-matching `MODALITY_KEYWORDS` against the real parcel names.

**Verified locally** with a synthetic `(19, 20484)` array: produces `(19, 200)` parcels,
all 200 non-zero, and visual=29 / audio=35 / language=45 parcels matched.

---

## Step 1 — Get the real parcel names

```bash
pip3 install nibabel numpy
```

Download the annot files (use curl — macOS system Python has SSL cert issues with urllib):
```bash
mkdir -p /tmp/schaefer_fs5 && cd /tmp/schaefer_fs5
BASE="https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master/stable_projects/brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/FreeSurfer5.3/fsaverage5/label"
curl -sSL -o lh.Schaefer2018_200Parcels_7Networks_order.annot "$BASE/lh.Schaefer2018_200Parcels_7Networks_order.annot"
curl -sSL -o rh.Schaefer2018_200Parcels_7Networks_order.annot "$BASE/rh.Schaefer2018_200Parcels_7Networks_order.annot"
```

Print all 200 names:
```python
import nibabel as nib
names = []
for h in ("lh", "rh"):
    _, _, n = nib.freesurfer.io.read_annot(f"/tmp/schaefer_fs5/{h}.Schaefer2018_200Parcels_7Networks_order.annot")
    names += [x.decode() for x in n[1:101]]   # skip medial-wall entry
for i, x in enumerate(names): print(i, x)
```

Names follow `7Networks_LH_Vis_1`, `7Networks_RH_SomMot_3`,
`7Networks_LH_Default_Temp_2`, `7Networks_RH_Cont_PFCl_1`, etc.

---

## Step 2 — Verify / refine MODALITY_KEYWORDS

Map each network to a modality:

| Modality | Network keywords | Rationale |
|---|---|---|
| Visual | `Vis` | Visual network = occipital + visual association cortex |
| Audio | `SomMot` | Schaefer folds auditory cortex into the somatomotor network (no separate `Aud`) |
| Language | `Default_Temp`, `Default_PFC`, `Cont_Temp`, `Cont_PFCl` | Temporal + lateral-PFC parcels ≈ Wernicke's / Broca's / language network |

Check the matches and counts:
```python
KW = {"visual": ["Vis"], "audio": ["SomMot"],
      "language": ["Default_Temp","Default_PFC","Cont_Temp","Cont_PFCl"]}
for m, kws in KW.items():
    hits = [n for n in names if any(k in n for k in kws)]
    print(f"{m}: {len(hits)} parcels — e.g. {hits[:3]}")
```

Decide if the language grouping is too broad/narrow (it's the fuzziest — DMN and
control-network temporal/PFC parcels are a proxy for the language network). If you tighten
it, prefer adding/removing whole network-region keywords over hand-listing indices, so the
mapping stays readable and robust to parcel re-ordering.

### Required audit pass

Before Blue Agent scores any reference videos, perform and report a short audit of the
current grouping. This is the fix for the current risk: the atlas plumbing works, but the
modality groupings are still provisional until this audit is completed.

Audit checklist:

- Print the parcel count for each modality.
- Print at least 3 example parcel names for each modality.
- Print any Schaefer network/region labels that are not assigned to visual/audio/language.
- Confirm whether `SomMot` is acceptable as the audio proxy for this demo, since Schaefer-7
  has no separate auditory network.
- Confirm whether the language keywords are too broad or too narrow:
  - `Default_Temp`
  - `Default_PFC`
  - `Cont_Temp`
  - `Cont_PFCl`
- If the language grouping changes, explain why in one sentence.
- Do not claim polished named brain regions from Schaefer labels alone. Schaefer names are
  atlas/network labels; user-facing labels may need a later translation layer.

Recommended output artifact:

Create a small metadata file after the audit, for example:

```text
results/schaefer200_modality_mapping.json
```

It should include:

```json
{
  "atlas": "Schaefer2018_200Parcels_7Networks_order fsaverage5 surface",
  "parcel_names": ["...200 names..."],
  "modality_keywords": {
    "visual": ["Vis"],
    "audio": ["SomMot"],
    "language": ["Default_Temp", "Default_PFC", "Cont_Temp", "Cont_PFCl"]
  },
  "modality_indices": {
    "visual": [],
    "audio": [],
    "language": []
  },
  "audit_notes": {
    "audio_proxy": "...",
    "language_scope": "...",
    "unassigned_networks": []
  }
}
```

This metadata can be used to interpret saved `parcels` arrays from existing runs without
rerunning Tribe inference.

---

## Step 3 — Update resonate_tribe_modal.py (only if refining)

Edit the `MODALITY_KEYWORDS` dict in place. Keep the explanatory comment above it accurate.
Do **not** reintroduce a hardcoded `MODALITY_REGIONS` index list — the keyword approach is
intentional so the grouping survives any change in parcel order or count.

---

## Step 4 — Sanity check (no GPU, $0)

```python
import numpy as np
# reuse _load_schaefer_fs5 + apply_atlas logic from resonate_tribe_modal.py
preds = np.random.randn(19, 20484).astype(np.float32)
res = apply_atlas(preds)
assert res["parcels"].shape == (19, 200)
for m in ("visual","audio","language"):
    assert len(res["modality_indices"][m]) > 0
print("OK")
```

(There is a ready-made version of this at `/Users/foramshah/modal_test/test_atlas_local.py`.)

---

## Done — report back
- Parcel counts per modality + 3 example names each
- Whether you changed `MODALITY_KEYWORDS` and why
- Confirm the local sanity check passes
