"""Sequential text-to-video pipeline optimized for the MacBook M2."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

import gc

from . import (
    text_to_image,
    image_to_video,
    audio_generation,
    lip_sync,
    assembly,
)


def generate_video_from_text(
    prompt: str,
    output_path: str,
    *,
    style: str = "photographic",
    aspect_ratio: str = "1:1",
    motion: str = "pan",
    voice: str = "female",
    music_style: str = "ambient",
    preview: bool = False,
    progress_callback: Callable[[str], None] | None = None,
) -> str:
    """Run the entire pipeline from text prompt to final video file.

    Set ``preview=True`` to generate a quick 1-second draft video.
    Returns the path to the generated video.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = Path(output_path)
    tmp_video = base.with_name(f"{base.stem}_{timestamp}_image.mp4")
    speech_file = base.with_name(f"{base.stem}_{timestamp}_speech.mp3")
    music_file = base.with_name(f"{base.stem}_{timestamp}_music.mp3")

    image = text_to_image.generate_image(
        prompt, style=style, aspect_ratio=aspect_ratio
    )
    if progress_callback:
        progress_callback("image")
    video_path = image_to_video.generate_video(
        image,
        motion=motion,
        output_path=tmp_video.as_posix(),
        preview=preview,
    )
    del image
    gc.collect()
    if progress_callback:
        progress_callback("video")
    speech_path = audio_generation.generate_voice(
        prompt, voice=voice, output_path=speech_file.as_posix()
    )
    if progress_callback:
        progress_callback("speech")
    music_path = audio_generation.generate_music(
        style=music_style, output_path=music_file.as_posix()
    )
    if progress_callback:
        progress_callback("music")

    mixed_audio: Optional[str]
    if speech_path and music_path:
        from moviepy.editor import (
            AudioFileClip,
            CompositeAudioClip,
        )

        mixed_file = base.with_name(f"{base.stem}_{timestamp}_mix.mp3")
        speech_clip = AudioFileClip(speech_path)
        music_clip = AudioFileClip(music_path).volumex(0.5)
        composite = CompositeAudioClip([music_clip, speech_clip])
        composite.write_audiofile(
            mixed_file.as_posix(), verbose=False, logger=None
        )
        speech_clip.close()
        music_clip.close()
        composite.close()
        mixed_audio = mixed_file.as_posix()
    else:
        mixed_audio = speech_path or music_path

    if progress_callback:
        progress_callback("audio_mixed")

    synced_video_path = lip_sync.apply_lip_sync(video_path, speech_path)
    if progress_callback:
        progress_callback("lip_sync")
    assembly.assemble_video(synced_video_path, mixed_audio, output_path)
    if progress_callback:
        progress_callback("assembly")
    del video_path
    gc.collect()
    del speech_path
    del music_path
    gc.collect()
    if progress_callback:
        progress_callback("done")
    return output_path
