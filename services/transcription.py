"""
Transcription service using Anthropic's Audio API.
Transcribes audio files to text using Claude.
"""

import os
import base64
import anthropic


def transcribe_audio(audio_path: str, api_key: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Transcribe an audio file using Anthropic's Audio API.

    Args:
        audio_path: Path to the audio file (WAV)
        api_key: Anthropic API key
        model: Claude model to use

    Returns:
        Transcription text
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not api_key:
        raise ValueError("API key is required for transcription")

    # Create Anthropic client
    client = anthropic.Anthropic(api_key=api_key)

    # Read and encode audio file to base64
    with open(audio_path, 'rb') as audio_file:
        audio_data = base64.standard_b64encode(audio_file.read()).decode('utf-8')

    print(f"[TRANSCRIPTION DEBUG] Audio file: {audio_path}")
    print(f"[TRANSCRIPTION DEBUG] File size: {os.path.getsize(audio_path)} bytes")

    # Transcribe using Claude's document/audio API
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "audio/wav",
                            "data": audio_data
                        }
                    },
                    {
                        "type": "text",
                        "text": "Please transcribe this audio recording. Provide only the transcription text, nothing else."
                    }
                ]
            }
        ]
    )

    transcription = message.content[0].text.strip()
    print(f"[TRANSCRIPTION DEBUG] Raw transcription: '{transcription}'")
    print(f"[TRANSCRIPTION DEBUG] Transcription length: {len(transcription)}")
    
    return transcription
