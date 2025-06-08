"""Final video assembly using ``moviepy``."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from moviepy.editor import AudioFileClip, VideoFileClip


def assemble_video(
    video_path: str,
    audio_path: Optional[str],
    output_path: str,
) -> None:
    """Combine video and optional audio into the final file."""

    path = Path(output_path)
    clip = VideoFileClip(video_path)
    if audio_path:
        audio_clip = AudioFileClip(audio_path)
        clip = clip.set_audio(audio_clip)
    clip.write_videofile(
        path.as_posix(), codec="libx264", fps=24, verbose=False, logger=None
    )
    clip.close()
    if audio_path:
        audio_clip.close()
