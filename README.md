# Prompt Video Pipeline

This repository contains a skeleton implementation of a text-to-video
pipeline optimized for the MacBook Pro M2. The goal is to demonstrate an
architecture capable of converting text prompts into short multimedia
videos using a sequence of lightweight processing steps.

The current implementation contains a working text-to-image generator
using Stable Diffusion through the `diffusers` library. Style presets,
aspect ratio options and a simple upscaling step are implemented. The
remaining stages are placeholders and should be expanded with Apple
Silicon optimizations as described in the project specification.

## Structure

- `src/prompt_video/` – Python package with pipeline modules
- `pyproject.toml` – project configuration and dependencies

## Running

Install dependencies (including PyTorch and Diffusers) and start the FastAPI server:

```bash
pip install -e .
uvicorn prompt_video.main:app --reload
```

Then send a POST request to `/generate` with a JSON body containing your
prompt and optional parameters:

```json
{
  "prompt": "a tranquil forest",
  "style": "cinematic",
  "aspect_ratio": "16:9"
}
```

The server responds with the path to the generated video (placeholder
until later phases are implemented).

