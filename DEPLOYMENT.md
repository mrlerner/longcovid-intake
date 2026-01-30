# Deploying to Railway

This guide will help you deploy the Long-COVID Intake application to Railway.

## Prerequisites

1. A [Railway](https://railway.app/) account
2. An Anthropic API key for Claude

## Deployment Steps

### 1. Prepare Your Repository

Ensure all required files are committed to your Git repository:
- `app.py` - Main Flask application
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `Procfile` - Tells Railway how to start your app
- `railway.json` - Railway-specific configuration
- `services/` - Service modules (audio, transcription, analysis)
- `static/` and `templates/` - Frontend assets

### 2. Create a New Railway Project

1. Go to [Railway](https://railway.app/) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will automatically detect it's a Python app and use the Procfile

### 3. Configure Environment Variables

In your Railway project dashboard, go to the "Variables" tab and add:

```
CLAUDE_API_KEY=your_actual_anthropic_api_key
CLAUDE_MODEL=claude-sonnet-4-20250514
SECRET_KEY=generate_a_random_secret_key_here
FLASK_ENV=production
```

**Important Notes:**
- `PORT` is automatically set by Railway - don't add it manually
- Generate a strong random string for `SECRET_KEY` (e.g., use Python: `python -c "import secrets; print(secrets.token_hex(32))"`)
- Get your `CLAUDE_API_KEY` from the [Anthropic Console](https://console.anthropic.com/)

### 4. Deploy

1. Railway will automatically build and deploy your app
2. Once deployed, Railway will provide a public URL (e.g., `your-app.up.railway.app`)
3. Visit the URL to test your application

### 5. Monitor Deployment

- Check the "Deployments" tab for build logs
- Check the "Observability" tab for runtime logs
- If there are errors, review logs and adjust environment variables or code as needed

## Important Considerations

### File Storage

The current app uses local filesystem storage for uploaded videos and audio files. This works on Railway, but note:

- **Files are ephemeral**: Railway containers can restart, and uploaded files will be lost
- **Not suitable for long-term storage**: For production, consider:
  - Using Railway's volume mounts for persistent storage
  - Uploading to S3, Cloudflare R2, or similar object storage
  - Implementing a proper database for session management

### Session Management

The app currently uses in-memory session storage (`patient_sessions` dict). This means:

- Sessions are lost when the app restarts
- Not suitable for multi-instance deployments
- For production, consider using Redis or a database

### Performance

The app uses:
- **Whisper** for audio transcription (runs locally in the container)
- **Claude API** for symptom analysis

Railway's default plan should handle this, but monitor:
- Memory usage (Whisper model requires ~1-2GB RAM)
- CPU usage during transcription
- API rate limits from Anthropic

### Costs

- Railway: Check their [pricing page](https://railway.app/pricing)
- Anthropic API: Pay-per-token usage based on Claude API calls

## Testing

1. Visit your Railway URL
2. Start a new session
3. Record responses to the three questions
4. Verify transcription works
5. Check that symptom analysis completes successfully

## Troubleshooting

### Build Fails

- Check that all dependencies in `requirements.txt` are valid
- Review build logs in Railway dashboard
- Ensure Python version compatibility (Railway uses Python 3.11+ by default)

### Runtime Errors

- Check environment variables are set correctly
- Review runtime logs in Railway dashboard
- Test locally first with `gunicorn app:app` to verify production server works

### Slow Performance

- Whisper transcription can take 10-30 seconds per video
- Consider upgrading Railway plan for more CPU/RAM
- Consider using Anthropic's batch API or optimizing prompts

## Local Testing with Production Settings

To test locally with production settings:

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp env.example .env
# Edit .env with your actual values

# Run with gunicorn (production server)
gunicorn app:app --bind 0.0.0.0:8085

# Or run with Flask (development)
python app.py
```

## Railway-Specific Features

### Custom Domain

- Go to Settings → Domains in Railway dashboard
- Add your custom domain
- Update DNS records as instructed

### Scaling

- Railway supports horizontal scaling
- For multi-instance deployments, you'll need to implement:
  - Shared session storage (Redis, database)
  - Shared file storage (S3, etc.)

### Environment-Specific Configuration

You can use Railway's "Environments" feature to maintain separate staging/production deployments.

## Support

- Railway Docs: https://docs.railway.app/
- Anthropic Docs: https://docs.anthropic.com/
- Report issues with this app: [Your GitHub Issues URL]
