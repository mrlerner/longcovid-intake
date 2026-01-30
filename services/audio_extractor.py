"""
Audio extraction service.
Extracts audio track from video files for transcription.
"""

import os
import subprocess
import imageio_ffmpeg


def extract_audio(video_path: str) -> str:
    """
    Extract audio from a video file and save as WAV.

    Args:
        video_path: Path to the video file (WebM)

    Returns:
        Path to the extracted audio file (WAV)
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    # Generate audio output path
    base_path = os.path.splitext(video_path)[0]
    audio_path = f"{base_path}_audio.wav"

    # Get ffmpeg path from imageio_ffmpeg (bundled)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    # Use ffmpeg directly to extract audio
    # -y: overwrite output file
    # -i: input file
    # -vn: no video
    # -acodec pcm_s16le: 16-bit PCM audio
    # -ar 44100: 44.1kHz sample rate
    # -ac 1: mono channel
    cmd = [
        ffmpeg_path,
        '-y',
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '44100',
        '-ac', '1',
        audio_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("FFmpeg not found. Please install ffmpeg.")

    if not os.path.exists(audio_path):
        raise RuntimeError("Audio extraction failed - output file not created")

    return audio_path
