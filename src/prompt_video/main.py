"""FastAPI app exposing the text-to-video pipeline."""

import asyncio
import logging # Added
from datetime import datetime
from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel

from . import pipeline

# Configure basic logging
# It's often better to configure logging once at the application entry point.
# However, basicConfig in startup is also common for FastAPI.
# For more complex scenarios, a logging config file or dict is preferred.

logger = logging.getLogger(__name__) # Added logger instance

app = FastAPI(title="Prompt Video Pipeline")

_tasks: Dict[str, Dict[str, Any]] = {}
_queue: asyncio.Queue = asyncio.Queue()


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "photographic"
    aspect_ratio: str = "1:1"
    motion: str = "pan"
    voice: str = "female_1"
    music_style: str = "ambient"
    preview: bool = False


async def _worker() -> None:
    while True:
        task_id, req, output_path = await _queue.get()
        logger.info(f"Processing task {task_id} for prompt: '{req.prompt}'") # Added

        def update(stage: str) -> None:
            logger.info(f"Task {task_id} reached stage: {stage}") # Added
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
            logger.info(f"Task {task_id} completed successfully. Output: {out}") # Added
        except Exception as exc:  # pragma: no cover - simple logging
            logger.error(f"Error processing task {task_id}: {exc}", exc_info=True) # Modified
            _tasks[task_id]["status"] = "error"
            _tasks[task_id]["error"] = str(exc)
        _queue.task_done()


@app.on_event("startup")
async def _startup() -> None:
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Get a logger for this module after basicConfig is set
    # (though logger defined at top level will also use this config once set)
    startup_logger = logging.getLogger(__name__)
    startup_logger.info("FastAPI application startup complete. Logging configured.")
    asyncio.create_task(_worker())


@app.post("/generate")
async def generate(req: GenerateRequest):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output_{timestamp}.mp4"
    task_id = timestamp
    _tasks[task_id] = {"status": "queued", "output_path": None}
    await _queue.put((task_id, req, output_path))
    logger.info(f"Task {task_id} queued for prompt: '{req.prompt}'") # Added
    return {"task_id": task_id}


@app.get("/progress/{task_id}")
async def progress(task_id: str):
    task_info = _tasks.get(task_id, {"status": "unknown"})
    # logger.debug(f"Progress requested for task {task_id}: {task_info}") # Example of debug log
    return task_info
