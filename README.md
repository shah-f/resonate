# Resonate

**Know exactly where your video loses the brain.**

Resonate runs your short-form video through Meta's Tribe v2 brain encoding model to predict second-by-second cortical activation across 20,000+ brain surface vertices. It maps those signals onto the Schaefer-200 neuroscience atlas, separates them into visual, audio, and language engagement tracks, and delivers creator-ready coaching — all in under two minutes.

Built in 12 hours at the NYTW Intern Hackathon.

---

## What It Does

Upload a vertical video. Resonate:

1. **Runs Tribe v2 inference** on Modal GPU infrastructure — predicting how a human brain responds to every second of your content at the cortical level
2. **Maps 20,484 fsaverage5 surface vertices** to 200 named brain parcels using the Schaefer-200 atlas (Yeo lab, 7-network parcellation)
3. **Aggregates into three engagement modalities** — Visual, Audio, Language — based on neuroscientifically-validated region groupings
4. **Finds your dips, hooks, and CTA windows** — the exact timesteps where predicted engagement collapses, peaks, or plateaus
5. **Generates plain-language creator coaching** via GPT-4o, translating neuroscience signals into actionable fixes

---

## Demo

Five pre-analyzed clips load instantly — no upload required:

| Clip | Duration | Dominant Modality |
|---|---|---|
| Complaint TikTok | 15s | Audio |
| Finance Explainer | 11s | Language |
| GRWM | 16s | Visual |
| Walk in the Park | 15s | Visual |
| Flow State (Zetamac) | 14s | Audio |

---

## Architecture

```
Browser (Next.js 16)
    │
    ├── /api/analyze   → FastAPI (Python)
    │       │
    │       ├── Modal GPU  →  Tribe v2 inference (20,484 vertices × N timesteps)
    │       │                  ↓
    │       │              Schaefer-200 atlas mapping  →  200 parcel scores
    │       │                  ↓
    │       ├── resonate_analysis.py  →  modality tracks, dips, windows, feature cards
    │       └── resonate_llm_insights.py  →  GPT-4o coaching (optional)
    │
    └── /results/[jobId]  →  React results dashboard
            ├── 3D Brain (Three.js / React Three Fiber)  —  200 parcel nodes, live-animated
            ├── Attention Timeline
            ├── Modality Tracks (Visual / Audio / Language)
            ├── Feature Cards  —  Hook, Engagement Autopsy, Payoff, CTA Window, Balance
            └── Creator Feedback  —  LLM coaching markdown
```

---

## Tech Stack

### AI / Neuroscience
| Component | What it does |
|---|---|
| **Meta Tribe v2** | Brain encoding model — predicts fMRI-like cortical response from video |
| **Schaefer-200 Atlas** (Yeo lab, 7-network) | Maps 20,484 fsaverage5 surface vertices → 200 named brain parcels |
| **nibabel** | Reads `.annot` surface label files from the FreeSurfer/CBIG atlas |
| **GPT-4o** | Translates neuroscience evidence packets into creator coaching |

### Backend
| Component | What it does |
|---|---|
| **Modal** | Serverless GPU execution for Tribe v2 (A10G / T4) |
| **FastAPI + Uvicorn** | REST API server — job queue, status polling, video streaming |
| **NumPy** | Signal normalization, parcel averaging, window analysis |
| **PySceneDetect** | Local scene-cut detection for pacing analysis |

### Frontend
| Component | What it does |
|---|---|
| **Next.js 16** | App router, server components, API proxy routes |
| **React Three Fiber + Three.js** | 3D brain visualization — 200 animated parcel nodes with bloom post-processing |
| **@react-three/postprocessing** | Bloom effect on parcel activation |
| **TanStack Query** | Job status polling and result fetching |
| **Tailwind CSS v4** | Styling |
| **Framer Motion** | Transitions |
| **Radix UI** | Accessible UI primitives |
| **Recharts** | Timeline charts |
| **react-markdown + remark-gfm** | LLM coaching render |

---

## Running Locally

### Backend

```bash
# Install Python deps
pip install -r requirements.txt

# Start the API server (requires Modal auth)
python3 scripts/api_server.py
# → http://localhost:8000
```

Modal credentials must be configured (`modal token new`) and the `resonate` app must be deployed:

```bash
modal deploy resonate_tribe_modal.py
```

Set `OPENAI_API_KEY` to enable LLM coaching. Without it, the pipeline still runs — coaching cards are just omitted.

### Frontend

```bash
cd frontendStuff/resonate-app
pnpm install
pnpm dev
# → http://localhost:3000
```

Set `PYTHON_API_URL` in `.env.local` if the backend runs on a non-default port:

```
PYTHON_API_URL=http://localhost:8000
```

---

## Pipeline Details

### Tribe v2 Inference
Tribe v2 is a video-to-brain encoding model trained on fMRI data from humans watching naturalistic video. It produces per-vertex activation predictions on the fsaverage5 cortical surface mesh — the same coordinate space used in human neuroimaging studies. Resonate uses Modal to run this inference on-demand with no local GPU required.

### Schaefer-200 Atlas Mapping
Raw vertex predictions are averaged within each of the 200 Schaefer parcels using the fsaverage5 `.annot` files from the CBIG/Yeo lab. Parcels are grouped into three modality tracks by region name:

- **Visual** — parcels matching `Vis` (visual cortex networks)
- **Audio** — parcels matching `SomMot` (somatomotor, which includes auditory cortex in this parcellation)
- **Language** — parcels matching `Default_Temp`, `Default_PFC`, `Cont_Temp`, `Cont_PFCl` (default mode and control networks implicated in language and semantic processing)

### Analysis
`resonate_analysis.py` is fully deterministic — no model calls. It normalizes modality tracks to 0–100, computes a weighted overall engagement score, identifies attention dips (timesteps with the steepest drops), finds the optimal CTA window (earliest high-attention moment), and generates structured evidence packets for each insight card.

---

## Repository Layout

```
brain/
├── resonate_tribe_modal.py        # Modal app — Tribe v2 inference + atlas mapping
├── scripts/
│   ├── api_server.py              # FastAPI server
│   └── insights_to_result.py     # Converts insights JSON → ResonateResult shape
├── analysis/
│   ├── resonate_analysis.py       # Deterministic signal analysis
│   ├── resonate_llm_insights.py   # GPT-4o coaching generation
│   └── resonate_llm_prompt.py     # Prompt builder
├── modal_test/
│   └── test_inference.py          # Run inference on a local video
├── results/                       # Generated inference + insights artifacts
├── test_clips/                    # Sample input videos
└── frontendStuff/resonate-app/    # Next.js frontend
    ├── app/                       # App router pages + API routes
    ├── components/                # UI components incl. brain-visualization.tsx
    └── lib/library/               # Pre-generated results for demo clips
```
