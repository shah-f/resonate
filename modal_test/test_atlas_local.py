"""Local $0 test of the surface Schaefer-200 atlas mapping — no GPU, no Modal."""
import os, sys, urllib.request
import numpy as np
import nibabel as nib

SCHAEFER_FS5_BASE = (
    "https://raw.githubusercontent.com/ThomasYeoLab/CBIG/master/stable_projects/"
    "brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/FreeSurfer5.3/"
    "fsaverage5/label"
)
SCHAEFER_FS5_FILES = {
    "lh": "lh.Schaefer2018_200Parcels_7Networks_order.annot",
    "rh": "rh.Schaefer2018_200Parcels_7Networks_order.annot",
}
MODALITY_KEYWORDS = {
    "visual":   ["Vis"],
    "audio":    ["SomMot"],
    "language": ["Default_Temp", "Default_PFC", "Cont_Temp", "Cont_PFCl"],
}


def _load_schaefer_fs5(cache_dir="/tmp/schaefer_fs5"):
    os.makedirs(cache_dir, exist_ok=True)
    hemi_labels, hemi_names = {}, {}
    for hemi, fname in SCHAEFER_FS5_FILES.items():
        path = os.path.join(cache_dir, fname)
        if not os.path.exists(path):
            print(f"downloading {fname} ...")
            urllib.request.urlretrieve(f"{SCHAEFER_FS5_BASE}/{fname}", path)
        labels, _ctab, names = nib.freesurfer.io.read_annot(path)
        hemi_labels[hemi] = labels
        hemi_names[hemi] = [n.decode() if isinstance(n, bytes) else n for n in names]
        print(f"{hemi}: labels shape={labels.shape}, n_names={len(names)}, "
              f"label range={labels.min()}..{labels.max()}")
    parcel_names = hemi_names["lh"][1:101] + hemi_names["rh"][1:101]
    return hemi_labels["lh"], hemi_labels["rh"], parcel_names


def apply_atlas(preds):
    n_timesteps, n_vertices = preds.shape
    per_hemi = n_vertices // 2
    lh_lab, rh_lab, parcel_names = _load_schaefer_fs5()
    lh_pred = preds[:, :per_hemi]
    rh_pred = preds[:, per_hemi:]
    parcel_scores = np.zeros((n_timesteps, 200))
    for p in range(1, 101):
        m = lh_lab == p
        if m.any():
            parcel_scores[:, p - 1] = lh_pred[:, m].mean(axis=1)
        m = rh_lab == p
        if m.any():
            parcel_scores[:, 100 + p - 1] = rh_pred[:, m].mean(axis=1)
    modality_indices = {m: [] for m in MODALITY_KEYWORDS}
    for idx, name in enumerate(parcel_names):
        for modality, keywords in MODALITY_KEYWORDS.items():
            if any(kw in name for kw in keywords):
                modality_indices[modality].append(idx)
    modality_scores = {}
    for modality, indices in modality_indices.items():
        modality_scores[modality] = (
            parcel_scores[:, indices].mean(axis=1) if indices else np.zeros(n_timesteps)
        )
    return {
        "parcels": parcel_scores,
        "visual": modality_scores["visual"],
        "audio": modality_scores["audio"],
        "language": modality_scores["language"],
        "parcel_names": parcel_names,
        "modality_indices": modality_indices,
    }


if __name__ == "__main__":
    # First confirm the annot vertex count matches fsaverage5 (10242/hemi)
    lh_lab, rh_lab, names = _load_schaefer_fs5()
    n_vert = len(lh_lab) + len(rh_lab)
    print(f"\ntotal surface vertices from annot: {n_vert} (expect 20484)")
    print(f"n parcel names: {len(names)} (expect 200)")
    print("sample names:", names[:3], "...", names[98:102])

    preds = np.random.randn(19, n_vert).astype(np.float32)
    res = apply_atlas(preds)
    print("\nparcels shape:", res["parcels"].shape, "(expect (19, 200))")
    for m in ("visual", "audio", "language"):
        idxs = res["modality_indices"][m]
        print(f"{m:9s}: {len(idxs):3d} parcels, "
              f"score mean={res[m].mean():.4f} shape={res[m].shape}")
    nonzero_parcels = (res["parcels"].sum(axis=0) != 0).sum()
    print(f"\nnon-zero parcels: {nonzero_parcels}/200")
    assert res["parcels"].shape == (19, 200), "parcels wrong shape"
    assert all(len(res["modality_indices"][m]) > 0 for m in ("visual","audio","language")), \
        "a modality has zero parcels — keyword matching failed"
    print("\n✅ LOCAL ATLAS TEST PASSED")
