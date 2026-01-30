# Long-COVID Intake Application

A Flask-based web application for capturing patient symptom information through video recordings, automatic transcription, and AI-powered symptom analysis.

## Features

- **Video Recording**: Patients can record video responses to intake questions directly in their browser
- **Automatic Transcription**: Uses OpenAI's Whisper model for speech-to-text conversion
- **AI Symptom Analysis**: Leverages Claude AI to analyze transcriptions and categorize symptoms
- **Session Management**: Tracks patient sessions throughout the intake process
- **Responsive UI**: Modern, user-friendly interface for easy patient interaction

## Technology Stack

- **Backend**: Flask (Python)
- **Transcription**: OpenAI Whisper
- **AI Analysis**: Anthropic Claude API
- **Frontend**: Vanilla JavaScript, HTML5 MediaRecorder API
- **Deployment**: Railway (or any WSGI-compatible platform)

## Prerequisites

- Python 3.8+
- FFmpeg (for audio extraction)
- Anthropic API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/longcovid-intake.git
cd longcovid-intake
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp env.example .env
```

Edit `.env` and add your configuration:
```
CLAUDE_API_KEY=your_anthropic_api_key_here
CLAUDE_MODEL=claude-sonnet-4-20250514
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:8085`

## Usage

1. **Start Session**: Navigate to the home page to begin a new patient intake session
2. **Record Responses**: Answer each question by recording a video response
3. **Transcription**: Videos are automatically transcribed after recording
4. **Analysis**: Once all questions are answered, the system analyzes symptoms and provides categorized results

### Test Mode

For quick testing with just one question, append `?test` to the URL:
```
http://localhost:8085?test
```

## Project Structure

```
longcovid-intake/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── Procfile             # Production server configuration
├── railway.json         # Railway deployment config
├── services/            # Core services
│   ├── audio_extractor.py   # Video to audio conversion
│   ├── transcription.py     # Whisper-based transcription
│   └── symptom_analyzer.py  # Claude-based symptom analysis
├── static/              # Frontend assets
│   ├── app.js          # Client-side JavaScript
│   └── style.css       # Styles
├── templates/
│   └── index.html      # Main UI template
└── uploads/            # Temporary storage for recordings (gitignored)
```

## Configuration

Key configuration options in `config.py`:

- **QUESTIONS**: The intake questions to ask patients
- **SYMPTOM_CATEGORIES**: Categories for symptom classification
- **CLAUDE_MODEL**: Which Claude model to use for analysis
- **UPLOAD_FOLDER**: Location for temporary file storage

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on deploying to Railway or other platforms.

### Quick Deploy to Railway

1. Push your code to GitHub
2. Connect your GitHub repository to Railway
3. Set environment variables in Railway dashboard
4. Deploy!

## API Endpoints

- `POST /api/session/start` - Initialize a new patient session
- `GET /api/session/state` - Get current session state
- `POST /api/video/upload` - Upload recorded video
- `POST /api/transcribe/<question_id>` - Transcribe a specific question
- `POST /api/transcribe/all` - Transcribe all recorded videos
- `POST /api/analyze` - Analyze symptoms from transcriptions
- `GET /api/summary` - Get complete session summary

## Development

### Running Tests

```bash
# Test mode with one question only
curl http://localhost:8085?test
```

### Debug Mode

The application includes debug logging. Check console output for detailed information about:
- Transcription results
- API calls
- File operations

## Important Notes

### File Storage

- Video and audio files are stored temporarily during processing
- Files are automatically cleaned up after transcription
- The `uploads/` directory is gitignored and should not be committed

### Session Management

- Current implementation uses in-memory session storage
- Sessions are lost when the application restarts
- For production, consider implementing Redis or database-backed sessions

### Privacy & HIPAA Compliance

This application handles potentially sensitive health information. Before using in production:

- Implement proper authentication and authorization
- Ensure encrypted data transmission (HTTPS)
- Add audit logging
- Review HIPAA compliance requirements
- Consider data retention policies
- Implement proper access controls

## Troubleshooting

### Whisper Model Downloads

On first run, Whisper will download language models (~1-2GB). This is normal and only happens once.

### FFmpeg Not Found

Install FFmpeg:
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Transcription Errors

- Check that video files contain actual audio
- Verify FFmpeg is installed and accessible
- Check console logs for detailed error messages

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please [create an issue](https://github.com/yourusername/longcovid-intake/issues) on GitHub.
