"""FastAPI app exposing the text-to-video pipeline."""

from fastapi import FastAPI
from pydantic import BaseModel

from . import pipeline

app = FastAPI(title="Prompt Video Pipeline")


class GenerateRequest(BaseModel):
    prompt: str
    style: str = "photographic"
    aspect_ratio: str = "1:1"
    motion: str = "pan"
    voice: str = "female"
    music_style: str = "ambient"


@app.post("/generate")
async def generate(req: GenerateRequest):
    output_path = "output.mp4"
    pipeline.generate_video_from_text(
        req.prompt,
        output_path,
        style=req.style,
        aspect_ratio=req.aspect_ratio,
        motion=req.motion,
        voice=req.voice,
        music_style=req.music_style,
    )
    return {"output_path": output_path}
