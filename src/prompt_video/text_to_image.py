"""Text-to-image generation optimized for the MacBook M2."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

import torch
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageStat


@lru_cache()
def _load_pipeline() -> StableDiffusionPipeline:
    """Load the Stable Diffusion pipeline once and cache it."""
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    pipe = pipe.to(device)
    pipe.safety_checker = None  # speed up
    return pipe


_STYLE_PRESETS: Dict[str, str] = {
    "photographic": "",
    "illustration": ", clean digital art",
    "animation": ", simple animation style",
    "cinematic": ", film still, cinematic lighting",
    "sketch": ", artistic sketch",
}


def _apply_style(prompt: str, style: str) -> str:
    suffix = _STYLE_PRESETS.get(style.lower(), "")
    return prompt + suffix


def _check_image_quality(image: Image.Image) -> bool:
    """Very small heuristic to detect nearly blank images."""
    stat = ImageStat.Stat(image)
    # Use average channel standard deviation as simple metric
    return max(stat.stddev) > 5


def generate_image(
    prompt: str,
    *,
    style: str = "photographic",
    aspect_ratio: str = "1:1",
    upscale_to: int | None = 768,
) -> Image.Image:
    """Generate an image from text using Stable Diffusion."""
    pipe = _load_pipeline()

    styled_prompt = _apply_style(prompt, style)
    width, height = 512, 512
    if aspect_ratio == "16:9":
        height = int(width * 9 / 16)
    elif aspect_ratio == "9:16":
        width = int(height * 9 / 16)

    result = pipe(prompt=styled_prompt, width=width, height=height, num_inference_steps=25)
    image = result.images[0]

    if not _check_image_quality(image):
        # One retry for extremely bad outputs
        result = pipe(prompt=styled_prompt, width=width, height=height, num_inference_steps=25)
        image = result.images[0]

    if upscale_to:
        image = image.resize((upscale_to, int(upscale_to * height / width)), Image.Resampling.LANCZOS)

    return image
