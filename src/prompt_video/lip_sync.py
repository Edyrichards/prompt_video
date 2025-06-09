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
import logging # Added
import subprocess

logger = logging.getLogger(__name__) # Added

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
        logger.info("No audio path provided for lip sync; returning original video.") # Added info
        return video_path

    if importlib.util.find_spec("wav2lip") is None:
        logger.info("Wav2Lip not installed; skipping lip sync.") # Modified
        return video_path

    base = Path(video_path)
    out_path = base.with_name(f"{base.stem}_lipsync.mp4")
    # Default checkpoint path, make it more visible/configurable if needed
    checkpoint_path = checkpoint or "wav2lip_gan.pth"

    logger.info(f"Attempting lip sync. Video: {video_path}, Audio: {audio_path}, Checkpoint: {checkpoint_path}") # Added info

    cmd = [
        "python",
        "-m",
        "wav2lip",
        "--checkpoint",
        checkpoint_path, # Use variable
        "--face",
        video_path,
        "--audio",
        audio_path,
        "--outfile",
        out_path.as_posix(),
        "--nosmooth", # Consider making this configurable too
    ]

    try:
        # It's good practice to capture stdout/stderr for better debugging if needed
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Wav2Lip completed successfully. Output video: {out_path.as_posix()}")
        logger.debug(f"Wav2Lip stdout: {result.stdout}") # Optional: log stdout if needed
    except subprocess.CalledProcessError as exc:
        logger.error(f"Wav2Lip failed with exit code {exc.returncode}. Error: {exc.stderr}", exc_info=True) # More specific error
        return video_path
    except Exception as exc:  # pragma: no cover - best effort
        logger.error(f"Wav2Lip failed with an unexpected error: {exc}", exc_info=True) # Modified
        return video_path

    return out_path.as_posix()
