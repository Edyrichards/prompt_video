"""Audio generation module optimized for Apple Silicon."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from gtts import gTTS


def generate_voice(
    text: str,
    voice: str = "female",
    *,
    lang: str = "en",
    output_path: str = "speech.mp3",
) -> str:
    """Generate speech audio from text using ``gTTS``.

    The ``voice`` argument is currently ignored but kept for API
    compatibility. ``gTTS`` requires internet access for synthesis.
    """

    tts = gTTS(text=text, lang=lang)
    path = Path(output_path)
    tts.save(path.as_posix())
    return path.as_posix()


def generate_music(style: str = "ambient", *, output_path: Optional[str] = None) -> Optional[str]:
    """Placeholder for background music generation."""

    print(f"Generating music in style: {style}")
    return output_path
