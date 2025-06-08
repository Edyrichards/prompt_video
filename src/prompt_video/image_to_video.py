"""Image-to-video generation optimized for Apple Silicon."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from moviepy.editor import ImageClip, vfx


def generate_video(
    image: Image.Image,
    motion: str = "pan",
    *,
    duration: int = 4,
    fps: int = 24,
    output_path: str = "image_video.mp4",
    preview: bool = False,
) -> str:
    """Generate a short video clip from a PIL image.

    This uses ``moviepy`` to create a lightweight animation. ``motion``
    currently supports ``pan`` (horizontal), ``tilt`` (vertical), and
    ``zoom``. In ``preview`` mode only a short 1-second clip is rendered.
    """

    if preview:
        duration = min(duration, 1)

    array = np.array(image)
    clip = ImageClip(array).set_duration(duration)

    if motion == "zoom":
        clip = clip.fx(vfx.resize, lambda t: 1 + 0.1 * (t / duration))
    elif motion == "pan":
        original_w = clip.w
        clip = clip.fx(vfx.resize, 1.1)
        pan_range = clip.w - original_w

        def crop_func(get_frame, t):
            x = int(pan_range * (t / duration))
            return get_frame(t)[:, x:x + original_w]

        clip = clip.fl(crop_func)
    elif motion == "tilt":
        original_h = clip.h
        clip = clip.fx(vfx.resize, 1.1)
        pan_range = clip.h - original_h

        def crop_func(get_frame, t):
            y = int(pan_range * (t / duration))
            return get_frame(t)[y:y + original_h, :]

        clip = clip.fl(crop_func)

    path = Path(output_path)
    clip.write_videofile(
        path.as_posix(),
        fps=fps,
        codec="libx264",
        audio=False,
        verbose=False,
        logger=None,
    )
    clip.close()
    return path.as_posix()
