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
) -> str:
    """Generate a short video clip from a PIL image.

    This uses ``moviepy`` to create a lightweight animation. ``motion``
    currently supports ``pan`` (subtle horizontal movement) and ``zoom``.
    """

    array = np.array(image)
    clip = ImageClip(array).set_duration(duration)

    if motion == "zoom":
        clip = clip.fx(vfx.resize, lambda t: 1 + 0.1 * (t / duration))
    elif motion == "pan":
        w = clip.w
        end = int(w * 0.1)

        def crop_func(get_frame, t):
            x = int(end * (t / duration))
            return get_frame(t)[:, x : x + w]

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
