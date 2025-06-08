"""FastAPI app exposing the text-to-video pipeline."""

import asyncio
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from . import pipeline

app = FastAPI(title="Prompt Video Pipeline")

_tasks: Dict[str, Dict[str, Any]] = {}
_queue: asyncio.Queue = asyncio.Queue()


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "photographic"
    aspect_ratio: str = "1:1"
    motion: str = "pan"
    voice: str = "female"
    music_style: str = "ambient"
    preview: bool = False


async def _worker() -> None:
    while True:
        task_id, req, output_path = await _queue.get()

        def update(stage: str) -> None:
            _tasks[task_id]["status"] = stage

        _tasks[task_id]["status"] = "running"
        try:
            out = await asyncio.to_thread(
                pipeline.generate_video_from_text,
                req.prompt,
                output_path,
                style=req.style,
                aspect_ratio=req.aspect_ratio,
                motion=req.motion,
                voice=req.voice,
                music_style=req.music_style,
                preview=req.preview,
                progress_callback=update,
            )
            _tasks[task_id]["status"] = "done"
            _tasks[task_id]["output_path"] = out
        except Exception as exc:  # pragma: no cover - simple logging
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)
        _queue.task_done()


@app.on_event("startup")
async def _startup() -> None:
    asyncio.create_task(_worker())


@app.post("/generate")
async def generate(req: GenerateRequest):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output_{timestamp}.mp4"
    task_id = timestamp
    _tasks[task_id] = {"status": "queued", "output_path": None}
    await _queue.put((task_id, req, output_path))
    return {"task_id": task_id}


@app.get("/progress/{task_id}")
async def progress(task_id: str):
    return _tasks.get(task_id, {"status": "unknown"})
