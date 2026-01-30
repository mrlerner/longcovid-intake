"""
Transcription service using OpenAI Whisper.
Transcribes audio files to text locally.
"""

import os
import ssl

# Workaround for SSL certificate issues when downloading model
ssl._create_default_https_context = ssl._create_unverified_context

import whisper

# Load model once at module level (lazy loading)
_model = None


def get_model():
    """Get or load the Whisper model."""
    global _model
    if _model is None:
        # Use 'base' model for good balance of speed and accuracy
        # Options: tiny, base, small, medium, large
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_path: str, api_key: str = None, model: str = None) -> str:
    """
    Transcribe an audio file using Whisper.

    Args:
        audio_path: Path to the audio file (WAV)
        api_key: Not used (kept for API compatibility)
        model: Not used (kept for API compatibility)

    Returns:
        Transcription text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # Load model
    whisper_model = get_model()

    # Transcribe
    result = whisper_model.transcribe(
        audio_path,
        language="en",  # Assume English for medical intake
        fp16=False  # Use FP32 for better compatibility
    )

    transcription = result["text"].strip()
    print(f"[WHISPER DEBUG] Audio file: {audio_path}")
    print(f"[WHISPER DEBUG] File size: {os.path.getsize(audio_path)} bytes")
    print(f"[WHISPER DEBUG] Raw transcription: '{transcription}'")
    print(f"[WHISPER DEBUG] Transcription length: {len(transcription)}")
    
    return transcription
