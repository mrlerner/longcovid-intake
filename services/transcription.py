"""
Transcription service using OpenAI Whisper.
Transcribes audio files to text.
"""

import os
import whisper

# Set Whisper cache directory to persist across builds
# This prevents re-downloading the model on each deploy
os.environ.setdefault("XDG_CACHE_HOME", "/app/.cache")

# Load model once at module level for efficiency
_model = None

def get_model(model_name: str = "base"):
    """Get or load the Whisper model."""
    global _model
    if _model is None:
        print(f"[TRANSCRIPTION] Loading Whisper model: {model_name}")
        print(f"[TRANSCRIPTION] Cache dir: {os.environ.get('XDG_CACHE_HOME', 'default')}")
        _model = whisper.load_model(model_name)
        print(f"[TRANSCRIPTION] Model loaded successfully")
    return _model


def transcribe_audio(audio_path: str, api_key: str = None, model: str = None) -> str:
    """
    Transcribe an audio file using OpenAI Whisper (local).

    Args:
        audio_path: Path to the audio file (WAV)
        api_key: Not used (kept for API compatibility)
        model: Not used (kept for API compatibility)

    Returns:
        Transcription text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"[TRANSCRIPTION DEBUG] Audio file: {audio_path}")
    print(f"[TRANSCRIPTION DEBUG] File size: {os.path.getsize(audio_path)} bytes")

    # Load model and transcribe
    whisper_model = get_model("base")

    result = whisper_model.transcribe(audio_path)
    transcription = result["text"].strip()

    print(f"[TRANSCRIPTION DEBUG] Raw transcription: '{transcription}'")
    print(f"[TRANSCRIPTION DEBUG] Transcription length: {len(transcription)}")

    return transcription
