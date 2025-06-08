"""Lip sync processing module optimized for Apple Silicon.

This implementation attempts to run the `Wav2Lip` command line
interface when available. If the package or its dependencies are not
installed, the function simply returns the original video path. The
`checkpoint` argument should point to a pre-trained ``.pth`` model file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import importlib.util
import subprocess


def apply_lip_sync(
    video_path: str,
    audio_path: Optional[str],
    *,
    checkpoint: str | None = None,
) -> str:
    """Apply lip sync to a video clip given speech audio.

    If ``Wav2Lip`` is not installed, the function prints a message and
    returns ``video_path`` unchanged. ``checkpoint`` should reference the
    model weights file required by Wav2Lip.
    """

    if audio_path is None:
        return video_path

    if importlib.util.find_spec("wav2lip") is None:
        print("Wav2Lip not installed; skipping lip sync")
        return video_path

    base = Path(video_path)
    out_path = base.with_name(f"{base.stem}_lipsync.mp4")
    cmd = [
        "python",
        "-m",
        "wav2lip",
        "--checkpoint",
        checkpoint or "wav2lip_gan.pth",
        "--face",
        video_path,
        "--audio",
        audio_path,
        "--outfile",
        out_path.as_posix(),
        "--nosmooth",
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as exc:  # pragma: no cover - best effort
        print(f"Wav2Lip failed: {exc}")
        return video_path

    return out_path.as_posix()
