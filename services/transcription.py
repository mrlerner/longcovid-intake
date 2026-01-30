"""
Transcription service using faster-whisper.
Uses CTranslate2 for 4x faster inference with 4x less memory than OpenAI Whisper.
"""

import os
from faster_whisper import WhisperModel

# Load model once at module level for efficiency
_model = None

def get_model(model_name: str = "base"):
    """Get or load the Whisper model."""
    global _model
    if _model is None:
        print(f"[TRANSCRIPTION] Loading faster-whisper model: {model_name}")
        # Use int8 quantization on CPU for best memory efficiency
        _model = WhisperModel(model_name, device="cpu", compute_type="int8")
        print(f"[TRANSCRIPTION] Model loaded successfully")
    return _model


def transcribe_audio(audio_path: str, api_key: str = None, model: str = None) -> str:
    """
    Transcribe an audio file using faster-whisper (local).

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

    segments, info = whisper_model.transcribe(audio_path, beam_size=5)

    # Collect all segment texts
    transcription = " ".join(segment.text for segment in segments).strip()

    print(f"[TRANSCRIPTION DEBUG] Raw transcription: '{transcription}'")
    print(f"[TRANSCRIPTION DEBUG] Transcription length: {len(transcription)}")

    return transcription
