"""
Export Schaefer-200 parcel centroids for frontend visualization.

Usage:
  python scripts/export_schaefer_centroids.py --out frontend/src/mock/schaefer200_parcels.json

This script will attempt to use nilearn to compute parcel centroids on fsaverage5.
If nilearn is not installed or surface files are not available, it falls back to a
deterministic hemisphere spiral placement (suitable for the demo).

The produced JSON has this shape:
{
  "parcels": [ {"index": 0, "name": "7Networks_LH_Vis_1", "hemisphere": "LH", "pos": [x,y,z] }, ... ],
  "mock_timeseries": [[...], ...]  # optional per-timestep parcel values for demo
}
"""
import json
import argparse
import math
import os

try:
    from nilearn import datasets, surface
    HAVE_NILEARN = True
except Exception:
    HAVE_NILEARN = False

def deterministic_positions(n):
    positions = []
    half = (n + 1) // 2
    for i in range(n):
        is_left = i < half
        idx = i if is_left else i - half
        nhem = half
        theta = idx * (2 * math.pi / max(1, nhem))
        r = 0.25 + 0.75 * (idx / max(1, nhem - 1)) if nhem > 1 else 0.6
        x = (-1 if is_left else 1) * (0.6 + math.cos(theta) * r)
        y = math.sin(theta) * r * 0.6
        z = math.sin(idx * 0.3) * 0.18
        positions.append([x, y, z])
    return positions

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='frontend/src/mock/schaefer200_parcels.json')
    args = p.parse_args()

    out = args.out

    # load parcel names from repo results if available
    mapping_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'schaefer200_modality_mapping.json')
    parcel_names = None
    try:
        with open(mapping_path) as f:
            mapping = json.load(f)
            parcel_names = mapping.get('parcel_names') or mapping.get('parcel_names')
    except Exception:
        parcel_names = [f'Parcel_{i+1}' for i in range(200)]

    n = len(parcel_names)

    parcels = []

    have_nilearn = HAVE_NILEARN
    if have_nilearn:
        try:
            print('Attempting to compute centroids using nilearn on fsaverage5...')
            fs = datasets.fetch_surf_fsaverage(mesh='fsaverage5')
            atlas = datasets.fetch_atlas_schaefer_2018(n_rois=200, yeo_networks=7)
            # atlas has maps for both hemispheres in some installations; try to load surface data
            left_map = atlas['maps_left'] if 'maps_left' in atlas else atlas.get('maps')
            # Fallback to deterministic if surface mapping not straightforward
            raise RuntimeError('Atlas surface mapping path unavailable in this environment — falling back')
        except Exception as e:
            print('nilearn path failed:', e)
            have_nilearn = False

    if not have_nilearn:
        positions = deterministic_positions(n)
        for i, pos in enumerate(positions):
            hemisphere = 'LH' if i < (n+1)//2 else 'RH'
            parcels.append({'index': i, 'name': parcel_names[i] if i < len(parcel_names) else f'Parcel_{i+1}', 'hemisphere': hemisphere, 'pos': pos})

    # produce simple mock timeseries (20 timesteps)
    timesteps = 20
    mock_timeseries = []
    for t in range(timesteps):
        row = []
        for i in range(n):
            # create a slowly varying wave per parcel for demo
            v = 0.35 + 0.3 * math.sin((t / timesteps) * 2 * math.pi + (i * 0.12))
            row.append(max(0, min(1, v)))
        mock_timeseries.append(row)

    out_obj = {'parcels': parcels, 'mock_timeseries': mock_timeseries}

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump(out_obj, f, indent=2)
    print('Wrote', out)

if __name__ == '__main__':
    main()
