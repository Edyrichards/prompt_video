"""Audio generation module optimized for Apple Silicon."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from gtts import gTTS
from moviepy.editor import AudioClip


_VOICE_PROFILES = {
    "female_1": {"lang": "en", "tld": "com"},
    "female_2": {"lang": "en", "tld": "co.uk"},
    "female_3": {"lang": "en", "tld": "ca"},
    "male_1": {"lang": "en", "tld": "com.au"},
    "male_2": {"lang": "en", "tld": "co.za"},
    "male_3": {"lang": "en", "tld": "ie"},
}


def generate_voice(
    text: str,
    voice: str = "female_1",
    *,
    lang: str = "en",
    output_path: str = "speech.mp3",
) -> str:
    """Generate speech audio from text using ``gTTS``.

    The ``voice`` argument selects among simple accent presets based on
    ``gTTS``'s ``tld`` option. Internet access is required for synthesis.
    """

    params = _VOICE_PROFILES.get(voice, {"lang": lang})
    tts = gTTS(
        text=text,
        lang=params.get("lang", lang),
        tld=params.get("tld", "com"),
    )
    path = Path(output_path)
    tts.save(path.as_posix())
    return path.as_posix()


def generate_music(
    style: str = "ambient",
    *,
    duration: int = 15,
    output_path: Optional[str] = None,
) -> Optional[str]:
    """Generate a simple tone as placeholder background music."""

    if output_path is None:
        return None

    frequency_map = {
        "ambient": 220,
        "upbeat": 440,
        "dramatic": 330,
        "peaceful": 250,
    }
    freq = frequency_map.get(style, 220)

    def make_frame(t: float) -> list[float]:
        return [0.2 * np.sin(2 * np.pi * freq * t)]

    clip = AudioClip(make_frame, duration=duration, fps=44100)
    path = Path(output_path)
    clip.write_audiofile(
        path.as_posix(), fps=44100, verbose=False, logger=None
    )
    clip.close()
    return path.as_posix()
