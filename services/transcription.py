"""
Transcription service using OpenAI Whisper.
Transcribes audio files to text.
"""

import os
import whisper

# Load model once at module level for efficiency
_model = None

def get_model(model_name: str = "base"):
    """Get or load the Whisper model."""
    global _model
    if _model is None:
        print(f"[TRANSCRIPTION] Loading Whisper model: {model_name}")
        _model = whisper.load_model(model_name)
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
