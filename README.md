# Prompt Video Pipeline

This repository contains a skeleton implementation of a text-to-video
pipeline optimized for the MacBook Pro M2. The goal is to demonstrate an
architecture capable of converting text prompts into short multimedia
videos using a sequence of lightweight processing steps.

The current implementation contains a working text-to-image generator
using Stable Diffusion through the `diffusers` library. The model loads
in half precision to reduce memory usage. Style presets, aspect ratio
options and a simple upscaling step are implemented.

Phase 3 begins with a lightweight image-to-video component based on
`moviepy` plus a TTS step using `gTTS` (which requires an internet
connection). Other stages remain placeholders and should be expanded
with Apple Silicon optimizations as described in the project
specification. The ``voice`` option now selects among six accent-based
presets.

Available voices:

- ``female_1`` – US accent
- ``female_2`` – UK accent
- ``female_3`` – Canadian accent
- ``male_1`` – Australian accent
- ``male_2`` – South African accent
- ``male_3`` – Irish accent

The image-to-video step supports ``pan`` (default), ``tilt`` and
``zoom`` motions. Use ``preview": true`` in your request to quickly
generate a 1-second draft clip before rendering the full video.

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
prompt and optional parameters. The server returns a task ID:

```json
{
  "prompt": "a tranquil forest",
  "style": "cinematic",
  "aspect_ratio": "16:9",
  "voice": "female_1",
  "motion": "tilt",
  "preview": true
}
```

```json
{"task_id": "20230101_123000"}
```

Check progress with `GET /progress/{task_id}`. When the status is
``done`` the response will include the ``output_path``.

Intermediate files created during processing are automatically deleted
after assembly to keep disk usage low.


## Gradio Interface

With the API server running you can launch a simple Gradio interface:

```bash
python ui.py
```

Fill in your prompt and options then click **Generate**. The interface
polls the API for progress and displays the resulting video when
finished.


The pipeline optionally applies lip sync using the `Wav2Lip` model if it
is installed. Provide a path to the model weights via the ``checkpoint``
parameter in ``lip_sync.apply_lip_sync`` or place ``wav2lip_gan.pth`` in
the current directory. When the package is missing, the step is skipped.

