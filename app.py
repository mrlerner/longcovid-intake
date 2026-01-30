import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Preload Whisper model at startup to avoid timeout on first request
print("[STARTUP] Preloading Whisper model...")
from services.transcription import get_model
get_model("base")
print("[STARTUP] Whisper model loaded successfully")

# In-memory session storage (in production: use Redis or database)
patient_sessions = {}


def cleanup_session_files(session_id):
    """Delete all remaining files in a session folder."""
    session_folder = os.path.join(Config.UPLOAD_FOLDER, session_id)
    if os.path.exists(session_folder):
        try:
            for filename in os.listdir(session_folder):
                file_path = os.path.join(session_folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(session_folder)
        except Exception as e:
            print(f"Warning: Could not clean up session folder {session_id}: {e}")


def get_session_data():
    """Get or create patient session data."""
    session_id = session.get('session_id')
    if session_id and session_id in patient_sessions:
        return patient_sessions[session_id]
    return None


def create_session(test_mode=False):
    """Create a new patient session."""
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id

    # Create session folder for uploads
    session_folder = os.path.join(Config.UPLOAD_FOLDER, session_id)
    os.makedirs(session_folder, exist_ok=True)

    patient_sessions[session_id] = {
        'session_id': session_id,
        'created_at': datetime.now().isoformat(),
        'status': 'in_progress',
        'test_mode': test_mode,
        'questions': {
            q['id']: {
                'question_id': q['id'],
                'title': q['title'],
                'text': q['text'],
                'video_path': None,  # Temporary - deleted after transcription
                'audio_path': None,  # Temporary - deleted after transcription
                'transcription': None,  # Persistent - kept in memory/database
                'recorded_at': None,
                'transcribed_at': None
            }
            for q in Config.QUESTIONS
        },
        'analysis': None
    }
    return patient_sessions[session_id]


# Routes
@app.route('/health')
def health_check():
    """Health check endpoint for Railway."""
    return jsonify({'status': 'healthy', 'whisper_loaded': True}), 200


@app.route('/')
def index():
    """Main intake page."""
    # Check for test mode via URL parameter
    test_mode = request.args.get('test') is not None
    return render_template('index.html',
                           clinic_name=Config.CLINIC_NAME,
                           questions=Config.QUESTIONS,
                           test_mode=test_mode)


@app.route('/api/session/start', methods=['POST'])
def start_session():
    """Initialize a new patient session."""
    # Check if test mode was requested
    test_mode = request.args.get('test') is not None
    session_data = create_session(test_mode=test_mode)
    return jsonify({
        'success': True,
        'session_id': session_data['session_id'],
        'questions': Config.QUESTIONS,
        'test_mode': test_mode
    })


@app.route('/api/session/state', methods=['GET'])
def get_session_state():
    """Get current session state."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    # Return simplified state for frontend
    questions_state = []
    for q in Config.QUESTIONS:
        q_data = session_data['questions'][q['id']]
        questions_state.append({
            'question_id': q['id'],
            'recorded': q_data['recorded_at'] is not None,  # Check if recording happened, not if file still exists
            'transcribed': q_data['transcription'] is not None
        })

    return jsonify({
        'session_id': session_data['session_id'],
        'status': session_data['status'],
        'questions': questions_state,
        'analysis': session_data['analysis']
    })


@app.route('/api/video/upload', methods=['POST'])
def upload_video():
    """Handle video upload for a question."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    question_id = request.form.get('question_id', type=int)

    if not question_id or question_id not in [1, 2, 3]:
        return jsonify({'error': 'Invalid question_id'}), 400

    if video_file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save video file
    session_folder = os.path.join(Config.UPLOAD_FOLDER, session_data['session_id'])
    filename = f"q{question_id}_video.webm"
    video_path = os.path.join(session_folder, filename)
    video_file.save(video_path)

    # Update session data
    session_data['questions'][question_id]['video_path'] = video_path
    session_data['questions'][question_id]['recorded_at'] = datetime.now().isoformat()

    return jsonify({
        'success': True,
        'question_id': question_id,
        'message': 'Video uploaded successfully'
    })


@app.route('/api/transcribe/<int:question_id>', methods=['POST'])
def transcribe_video(question_id):
    """Transcribe the video for a specific question."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    if question_id not in [1, 2, 3]:
        return jsonify({'error': 'Invalid question_id'}), 400

    q_data = session_data['questions'][question_id]
    if not q_data['video_path']:
        return jsonify({'error': 'No video recorded for this question'}), 400

    video_path = q_data['video_path']
    audio_path = None

    try:
        # Import services
        from services.audio_extractor import extract_audio
        from services.transcription import transcribe_audio

        # Extract audio from video
        audio_path = extract_audio(video_path)

        # Transcribe audio using Claude API
        transcription = transcribe_audio(audio_path, Config.CLAUDE_API_KEY, Config.CLAUDE_MODEL)
        q_data['transcription'] = transcription
        q_data['transcribed_at'] = datetime.now().isoformat()
        
        print(f"[DEBUG] Question {question_id} transcription: '{transcription}' (length: {len(transcription)})")

        # TESTING: Keep audio files for now to debug
        # Clean up: delete video file but KEEP audio for testing
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            # if audio_path and os.path.exists(audio_path):
            #     os.remove(audio_path)
            print(f"[DEBUG] Audio file saved at: {audio_path}")
        except Exception as cleanup_error:
            # Log but don't fail if cleanup fails
            print(f"Warning: Could not delete files: {cleanup_error}")

        # Clear file paths from session data since files are deleted
        q_data['video_path'] = None
        q_data['audio_path'] = None

        response_data = {
            'success': True,
            'question_id': question_id,
            'transcription': transcription
        }
        print(f"[DEBUG] Returning transcription response: {response_data}")
        return jsonify(response_data)

    except Exception as e:
        # If transcription fails, still try to clean up video but keep audio for debugging
        try:
            if video_path and os.path.exists(video_path):
                os.remove(video_path)
            # Keep audio file for debugging
            # if audio_path and os.path.exists(audio_path):
            #     os.remove(audio_path)
        except:
            pass
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcribe/all', methods=['POST'])
def transcribe_all():
    """Transcribe all recorded videos."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    results = {}
    errors = []

    for question_id in [1, 2, 3]:
        q_data = session_data['questions'][question_id]
        if not q_data['video_path']:
            errors.append(f"No video for question {question_id}")
            continue

        video_path = q_data['video_path']
        audio_path = None

        try:
            from services.audio_extractor import extract_audio
            from services.transcription import transcribe_audio

            # Extract audio
            audio_path = extract_audio(video_path)

            # Transcribe
            transcription = transcribe_audio(audio_path, Config.CLAUDE_API_KEY, Config.CLAUDE_MODEL)
            q_data['transcription'] = transcription
            q_data['transcribed_at'] = datetime.now().isoformat()

            results[question_id] = transcription

            # TESTING: Keep audio files for now to debug
            # Clean up: delete video file but KEEP audio for testing
            try:
                if os.path.exists(video_path):
                    os.remove(video_path)
                # if audio_path and os.path.exists(audio_path):
                #     os.remove(audio_path)
                print(f"[DEBUG] Audio file saved at: {audio_path}")
            except Exception as cleanup_error:
                print(f"Warning: Could not delete files for question {question_id}: {cleanup_error}")

            # Clear file paths from session data since files are deleted
            q_data['video_path'] = None
            q_data['audio_path'] = None

        except Exception as e:
            errors.append(f"Question {question_id}: {str(e)}")
            # Try to clean up video but keep audio for debugging
            try:
                if video_path and os.path.exists(video_path):
                    os.remove(video_path)
                # Keep audio for debugging
                # if audio_path and os.path.exists(audio_path):
                #     os.remove(audio_path)
            except:
                pass

    return jsonify({
        'success': len(errors) == 0,
        'transcriptions': results,
        'errors': errors if errors else None
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_symptoms():
    """Analyze all transcriptions for symptom clustering."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    # Check for test mode - only require question 1 if test param was passed
    test_mode = request.args.get('test') is not None or session_data.get('test_mode', False)
    required_questions = [1] if test_mode else [1, 2, 3]

    # Check required transcriptions are complete
    transcriptions = {}
    for question_id in required_questions:
        t = session_data['questions'][question_id]['transcription']
        if t is None:
            return jsonify({'error': f'Question {question_id} not yet transcribed'}), 400
        # Allow empty transcriptions (e.g., silent recordings) - use placeholder
        transcriptions[question_id] = t if t else "[No speech detected in recording]"

    try:
        from services.symptom_analyzer import analyze_symptoms

        print(f"[DEBUG] Analyzing transcriptions: {transcriptions}")
        print(f"[DEBUG] API Key present: {bool(Config.CLAUDE_API_KEY)}")
        print(f"[DEBUG] Number of symptom categories: {len(Config.SYMPTOM_CATEGORIES)}")
        print(f"[DEBUG] First category: {Config.SYMPTOM_CATEGORIES[0] if Config.SYMPTOM_CATEGORIES else 'NONE'}")

        analysis = analyze_symptoms(
            transcriptions,
            Config.CLAUDE_API_KEY,
            Config.CLAUDE_MODEL,
            Config.SYMPTOM_CATEGORIES
        )
        print(f"[DEBUG] Analysis result: {analysis}")
        print(f"[DEBUG] Has matched_categories: {'matched_categories' in analysis}")

        session_data['analysis'] = analysis
        session_data['status'] = 'completed'

        # Clean up any remaining files in the session folder
        cleanup_session_files(session_data['session_id'])

        return jsonify({
            'success': True,
            'analysis': analysis
        })

    except Exception as e:
        import traceback
        print(f"[ERROR] Analysis failed: {str(e)}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get complete session summary."""
    session_data = get_session_data()
    if not session_data:
        return jsonify({'error': 'No active session'}), 404

    summary = {
        'session_id': session_data['session_id'],
        'created_at': session_data['created_at'],
        'status': session_data['status'],
        'questions': []
    }

    for q in Config.QUESTIONS:
        q_data = session_data['questions'][q['id']]
        summary['questions'].append({
            'question_id': q['id'],
            'title': q['title'],
            'text': q['text'],
            'transcription': q_data['transcription']
        })

    summary['analysis'] = session_data['analysis']

    return jsonify(summary)


if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8085))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
