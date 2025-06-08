"""Sequential text-to-video pipeline optimized for the MacBook M2."""

from typing import Optional

from . import text_to_image, image_to_video, audio_generation, lip_sync, assembly


def generate_video_from_text(
    prompt: str,
    output_path: str,
    *,
    style: str = "photographic",
    aspect_ratio: str = "1:1",
    motion: str = "pan",
    voice: str = "female",
    music_style: str = "ambient",
) -> None:
    """Run the entire pipeline from text prompt to final video file."""
    image = text_to_image.generate_image(
        prompt, style=style, aspect_ratio=aspect_ratio
    )
    video_path = image_to_video.generate_video(image, motion=motion)
    speech_path = audio_generation.generate_voice(prompt, voice=voice)
    music_path = audio_generation.generate_music(style=music_style)
    # Placeholder: mix speech and music
    audio_track: Optional[str] = speech_path or music_path
    synced_video_path = lip_sync.apply_lip_sync(video_path, speech_path)
    assembly.assemble_video(synced_video_path, audio_track, output_path)
