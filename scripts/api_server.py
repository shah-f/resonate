"""Resonate API server — wraps Modal inference + analysis pipeline.

Usage:
    python3 scripts/api_server.py

Requires: fastapi, uvicorn, python-multipart
    pip install fastapi uvicorn python-multipart
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# Add scripts dir to path so insights_to_result is importable
sys.path.insert(0, str(Path(__file__).parent))
from insights_to_result import insights_to_result  # noqa: E402

BRAIN_DIR = Path(__file__).parent.parent
ANALYSIS_SCRIPT = BRAIN_DIR / "analysis" / "resonate_analysis.py"
LLM_SCRIPT = BRAIN_DIR / "analysis" / "resonate_llm_insights.py"
RESULTS_DIR = BRAIN_DIR / "results"
UPLOAD_DIR = Path(tempfile.gettempdir()) / "resonate_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

MESSAGES = [
    "Running Tribe v2...",
    "Mapping cortical vertices...",
    "Applying Schaefer-200 atlas...",
    "Finding attention dips...",
    "Generating creator feedback...",
]

app = FastAPI(title="Resonate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store: job_id -> {status, message, progress, result?, video_path?}
jobs: dict[str, dict[str, Any]] = {}


def _run_analysis(job_id: str, video_path: Path) -> None:
    """Background thread: Modal inference → deterministic analysis → LLM coaching."""
    try:
        stem = video_path.stem
        json_path = RESULTS_DIR / f"{stem}.json"
        insights_path = RESULTS_DIR / f"{stem}_insights.json"
        llm_md_path = RESULTS_DIR / f"{stem}_insights_llm_analysis.md"

        def update(msg: str, progress: float) -> None:
            jobs[job_id]["message"] = msg
            jobs[job_id]["progress"] = progress

        # Step 1: Modal inference (skip if cached)
        if json_path.exists():
            update("Using cached inference result...", 0.3)
        else:
            update(MESSAGES[0], 0.05)
            result = subprocess.run(
                ["python3", str(BRAIN_DIR / "modal_test" / "test_inference.py"), str(video_path)],
                capture_output=True, text=True, cwd=str(BRAIN_DIR),
            )
            if result.returncode != 0:
                raise RuntimeError(f"Modal inference failed:\n{result.stderr[-2000:]}")

        if not json_path.exists():
            raise RuntimeError(f"Inference artifact not found at {json_path}")

        # Step 2: Deterministic analysis
        update(MESSAGES[2], 0.55)
        result = subprocess.run(
            ["python3", str(ANALYSIS_SCRIPT), str(json_path), "--output", str(insights_path)],
            capture_output=True, text=True, cwd=str(BRAIN_DIR),
        )
        if result.returncode != 0:
            raise RuntimeError(f"Analysis failed:\n{result.stderr[-2000:]}")

        # Step 3: LLM coaching (optional — skip if no API key)
        llm_md = ""
        if os.environ.get("OPENAI_API_KEY") and not llm_md_path.exists():
            update(MESSAGES[4], 0.8)
            result = subprocess.run(
                ["python3", str(LLM_SCRIPT), str(insights_path)],
                capture_output=True, text=True, cwd=str(BRAIN_DIR),
            )
        if llm_md_path.exists():
            llm_md = llm_md_path.read_text()

        # Step 4: Convert to ResonateResult (include parcel data for 3D brain)
        insights = json.loads(insights_path.read_text())
        inference = json.loads(json_path.read_text())
        raw_parcels = inference.get("parcels")  # shape: (timesteps, 200)
        parcels_t = None
        if raw_parcels and len(raw_parcels) > 0 and len(raw_parcels[0]) > 0:
            # Transpose to (200, timesteps) as the frontend expects parcels[parcelIndex][timestep]
            n_parcels = len(raw_parcels[0])
            parcels_t = [[raw_parcels[t][p] for t in range(len(raw_parcels))] for p in range(n_parcels)]
        resonate_result = insights_to_result(insights, f"/api/video/{job_id}", llm_md, parcels=parcels_t)

        jobs[job_id].update({
            "status": "complete",
            "message": "Done",
            "progress": 1.0,
            "result": resonate_result,
            "video_path": str(video_path),
        })

    except Exception as exc:
        jobs[job_id].update({
            "status": "error",
            "message": str(exc)[:500],
            "progress": 0,
        })


@app.post("/analyze")
async def analyze(video: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    suffix = Path(video.filename or "video.mp4").suffix or ".mp4"
    video_path = UPLOAD_DIR / f"{job_id}{suffix}"
    video_path.write_bytes(await video.read())

    jobs[job_id] = {
        "status": "processing",
        "message": "Initializing...",
        "progress": 0.0,
        "startTime": time.time(),
    }

    threading.Thread(target=_run_analysis, args=(job_id, video_path), daemon=True).start()
    return {"jobId": job_id}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "status": job["status"],
        "message": job.get("message", ""),
        "progress": job.get("progress", 0),
    }


@app.get("/results/{job_id}")
def get_results(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] == "error":
        raise HTTPException(status_code=500, detail=job.get("message", "Analysis failed"))
    if job["status"] != "complete":
        raise HTTPException(status_code=202, detail="Job not complete yet")
    return job["result"]


@app.get("/video/{job_id}")
def get_video(job_id: str):
    job = jobs.get(job_id)
    if not job or "video_path" not in job:
        raise HTTPException(status_code=404, detail="Video not found")
    path = Path(job["video_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video file missing")
    media_type = "video/quicktime" if path.suffix == ".mov" else "video/mp4"
    return FileResponse(str(path), media_type=media_type)


@app.get("/health")
def health():
    return {"ok": True}


if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", "8000"))
    print(f"Resonate API server starting on http://localhost:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
