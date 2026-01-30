/**
 * Long-COVID Clinic Video Intake Application
 * Handles video recording, upload, and processing flow
 */

// Application State
const state = {
    currentScreen: 'welcome',
    currentQuestion: 1,
    totalQuestions: window.TEST_MODE ? 1 : 3,
    sessionId: null,
    mediaStream: null,
    mediaRecorder: null,
    recordedChunks: [],
    recordedBlobs: {},
    isRecording: false,
    recordingStartTime: null,
    timerInterval: null
};

// DOM Elements
const elements = {
    // Screens
    welcomeScreen: document.getElementById('welcome-screen'),
    cameraScreen: document.getElementById('camera-screen'),
    questionScreen: document.getElementById('question-screen'),
    processingScreen: document.getElementById('processing-screen'),
    completeScreen: document.getElementById('complete-screen'),

    // Welcome
    beginBtn: document.getElementById('begin-btn'),

    // Camera setup
    setupPreview: document.getElementById('setup-preview'),
    cameraStatus: document.getElementById('camera-status'),
    cameraReady: document.getElementById('camera-ready'),
    cameraError: document.getElementById('camera-error'),
    startQuestionsBtn: document.getElementById('start-questions-btn'),
    retryCameraBtn: document.getElementById('retry-camera-btn'),

    // Question screen
    progressFill: document.getElementById('progress-fill'),
    currentQuestionNum: document.getElementById('current-question-num'),
    questionTitle: document.getElementById('question-title'),
    questionText: document.getElementById('question-text'),
    recordingPreview: document.getElementById('recording-preview'),
    playbackVideo: document.getElementById('playback-video'),
    videoPlayButton: document.getElementById('video-play-button'),
    recordingIndicator: document.getElementById('recording-indicator'),
    recordingTimer: document.getElementById('recording-timer'),

    // Controls
    preRecordControls: document.getElementById('pre-record-controls'),
    recordingControls: document.getElementById('recording-controls'),
    postRecordControls: document.getElementById('post-record-controls'),
    startRecordingBtn: document.getElementById('start-recording-btn'),
    stopRecordingBtn: document.getElementById('stop-recording-btn'),
    rerecordBtn: document.getElementById('rerecord-btn'),
    continueBtn: document.getElementById('continue-btn'),

    // Progress steps
    steps: document.querySelectorAll('.step'),

    // Summary
    transcriptionsSummary: document.getElementById('transcriptions-summary'),
    analysisSummary: document.getElementById('analysis-summary')
};

// Initialize application
async function init() {
    setupEventListeners();
}

function setupEventListeners() {
    elements.beginBtn.addEventListener('click', handleBegin);
    elements.startQuestionsBtn.addEventListener('click', handleStartQuestions);
    elements.retryCameraBtn.addEventListener('click', handleRetryCamera);
    elements.startRecordingBtn.addEventListener('click', handleStartRecording);
    elements.stopRecordingBtn.addEventListener('click', handleStopRecording);
    elements.rerecordBtn.addEventListener('click', handleRerecord);
    elements.continueBtn.addEventListener('click', handleContinue);
    
    // Video playback controls
    elements.videoPlayButton.addEventListener('click', handleVideoPlayPause);
    elements.playbackVideo.addEventListener('click', handleVideoPlayPause);
    elements.playbackVideo.addEventListener('play', handleVideoPlay);
    elements.playbackVideo.addEventListener('pause', handleVideoPause);
    elements.playbackVideo.addEventListener('ended', handleVideoPause);
}

// Screen Navigation
function showScreen(screenName) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });

    const screenElement = document.getElementById(`${screenName}-screen`);
    if (screenElement) {
        screenElement.classList.add('active');
        state.currentScreen = screenName;
    }
}

// API Calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {}
    };

    if (data && !(data instanceof FormData)) {
        options.headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(data);
    } else if (data instanceof FormData) {
        options.body = data;
    }

    const response = await fetch(endpoint, options);
    return response.json();
}

// Welcome Screen Handlers
async function handleBegin() {
    // Start session (pass test mode if enabled)
    const endpoint = window.TEST_MODE ? '/api/session/start?test' : '/api/session/start';
    const result = await apiCall(endpoint, 'POST');
    if (result.success) {
        state.sessionId = result.session_id;
    }

    showScreen('camera');
    await initCamera();
}

// Camera Setup Handlers
async function initCamera() {
    elements.cameraStatus.classList.remove('hidden');
    elements.cameraReady.classList.add('hidden');
    elements.cameraError.classList.add('hidden');

    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                sampleRate: 44100
            }
        });

        state.mediaStream = stream;
        elements.setupPreview.srcObject = stream;

        elements.cameraStatus.classList.add('hidden');
        elements.cameraReady.classList.remove('hidden');

    } catch (error) {
        console.error('Camera access error:', error);
        elements.cameraStatus.classList.add('hidden');
        elements.cameraError.classList.remove('hidden');
    }
}

function handleRetryCamera() {
    initCamera();
}

function handleStartQuestions() {
    showScreen('question');
    elements.recordingPreview.srcObject = state.mediaStream;
    updateQuestionDisplay();
}

// Question Screen Handlers
function updateQuestionDisplay() {
    const question = window.QUESTIONS[state.currentQuestion - 1];

    elements.currentQuestionNum.textContent = state.currentQuestion;
    elements.questionTitle.textContent = question.title;
    elements.questionText.textContent = question.text;

    // Update progress
    const progress = ((state.currentQuestion - 1) / state.totalQuestions) * 100;
    if (elements.progressFill) {
        elements.progressFill.style.width = `${progress}%`;
    }

    // Update step indicators
    elements.steps.forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        if (stepNum < state.currentQuestion) {
            step.classList.add('completed');
        } else if (stepNum === state.currentQuestion) {
            step.classList.add('active');
        }
    });

    // Reset controls
    showControls('pre-record');

    // Show live preview
    elements.recordingPreview.classList.remove('hidden');
    elements.playbackVideo.classList.add('hidden');
    elements.videoPlayButton.classList.add('hidden');
}

function showControls(mode) {
    elements.preRecordControls.classList.add('hidden');
    elements.recordingControls.classList.add('hidden');
    elements.postRecordControls.classList.add('hidden');

    if (mode === 'pre-record') {
        elements.preRecordControls.classList.remove('hidden');
    } else if (mode === 'recording') {
        elements.recordingControls.classList.remove('hidden');
    } else if (mode === 'post-record') {
        elements.postRecordControls.classList.remove('hidden');
    }
}

// Recording Handlers
function handleStartRecording() {
    state.recordedChunks = [];

    // Determine supported mime type
    let mimeType = 'video/webm;codecs=vp9,opus';
    if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = 'video/webm;codecs=vp8,opus';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/webm';
        }
    }

    state.mediaRecorder = new MediaRecorder(state.mediaStream, { mimeType });

    state.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
            state.recordedChunks.push(event.data);
        }
    };

    state.mediaRecorder.onstop = () => {
        const blob = new Blob(state.recordedChunks, { type: mimeType });
        state.recordedBlobs[state.currentQuestion] = blob;

        // Show playback
        const url = URL.createObjectURL(blob);
        elements.playbackVideo.src = url;
        elements.playbackVideo.classList.remove('hidden');
        elements.recordingPreview.classList.add('hidden');
        
        // Show play button (video starts paused)
        elements.videoPlayButton.classList.remove('hidden');

        showControls('post-record');
    };

    state.mediaRecorder.start(1000); // Collect data every second
    state.isRecording = true;
    state.recordingStartTime = Date.now();

    // Show recording UI
    elements.recordingIndicator.classList.remove('hidden');
    showControls('recording');

    // Start timer
    updateTimer();
    state.timerInterval = setInterval(updateTimer, 1000);
}

function handleStopRecording() {
    if (state.mediaRecorder && state.isRecording) {
        state.mediaRecorder.stop();
        state.isRecording = false;

        // Stop timer
        clearInterval(state.timerInterval);
        elements.recordingIndicator.classList.add('hidden');
    }
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - state.recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    elements.recordingTimer.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function handleRerecord() {
    // Clear recorded blob
    delete state.recordedBlobs[state.currentQuestion];

    // Pause and hide playback video
    elements.playbackVideo.pause();
    elements.playbackVideo.classList.add('hidden');
    elements.videoPlayButton.classList.add('hidden');
    
    // Show live preview
    elements.recordingPreview.classList.remove('hidden');

    showControls('pre-record');
}

// Video playback handlers
function handleVideoPlayPause() {
    if (elements.playbackVideo.paused) {
        elements.playbackVideo.play();
    } else {
        elements.playbackVideo.pause();
    }
}

function handleVideoPlay() {
    elements.videoPlayButton.classList.add('hidden');
}

function handleVideoPause() {
    elements.videoPlayButton.classList.remove('hidden');
}

async function handleContinue() {
    // Upload the recorded video
    const blob = state.recordedBlobs[state.currentQuestion];
    if (!blob) {
        alert('No recording found. Please record your answer.');
        return;
    }

    // Show loading state
    elements.continueBtn.disabled = true;
    elements.continueBtn.textContent = 'Uploading...';

    try {
        const formData = new FormData();
        formData.append('video', blob, `q${state.currentQuestion}.webm`);
        formData.append('question_id', state.currentQuestion);

        const result = await apiCall('/api/video/upload', 'POST', formData);

        if (!result.success) {
            throw new Error(result.error || 'Upload failed');
        }

        // Move to next question or processing
        if (state.currentQuestion < state.totalQuestions) {
            state.currentQuestion++;
            updateQuestionDisplay();
        } else {
            // All questions done, start processing
            showScreen('processing');
            await processResponses();
        }

    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload video. Please try again.');
    } finally {
        elements.continueBtn.disabled = false;
        elements.continueBtn.innerHTML = `
            Continue
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 10h12M12 4l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    }
}

// Processing
async function processResponses() {
    const transcriptions = {};

    // Show complete screen early with loading states
    showCompleteScreenProgressive();

    // Transcribe each question (only those that were recorded)
    for (let i = 1; i <= state.totalQuestions; i++) {
        updateProcessingStep(i, 'active');

        try {
            const result = await apiCall(`/api/transcribe/${i}`, 'POST', {});
            if (result.success) {
                // Store transcription even if it's an empty string
                transcriptions[i] = result.transcription !== undefined ? result.transcription : null;
                updateProcessingStep(i, 'complete');
                
                // Update the transcription display immediately
                updateTranscriptionDisplay(i, transcriptions[i]);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error(`Transcription error for question ${i}:`, error);
            updateProcessingStep(i, 'error');
            updateTranscriptionDisplay(i, null, true);
        }
    }

    // Show analysis loading state
    showAnalysisLoading();

    // Analyze symptoms
    updateProcessingStep('analyze', 'active');

    try {
        const analysisResult = await apiCall('/api/analyze', 'POST', {});
        if (analysisResult.success) {
            updateProcessingStep('analyze', 'complete');

            // Update analysis display
            updateAnalysisDisplay(analysisResult.analysis);
        } else {
            throw new Error(analysisResult.error);
        }
    } catch (error) {
        console.error('Analysis error:', error);
        updateProcessingStep('analyze', 'error');

        // Show error message for analysis
        updateAnalysisDisplay(null, true);
    }

    // Stop camera stream
    if (state.mediaStream) {
        state.mediaStream.getTracks().forEach(track => track.stop());
    }
}

function updateProcessingStep(step, status) {
    const stepId = typeof step === 'number' ? `step-transcribe-${step}` : `step-${step}`;
    const stepElement = document.getElementById(stepId);
    if (!stepElement) return;

    const iconElement = stepElement.querySelector('.step-icon');

    stepElement.classList.remove('active', 'complete', 'error');
    iconElement.classList.remove('pending');

    if (status === 'active') {
        stepElement.classList.add('active');
        iconElement.innerHTML = '<div class="spinner small"></div>';
    } else if (status === 'complete') {
        stepElement.classList.add('complete');
        iconElement.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        `;
    } else if (status === 'error') {
        stepElement.classList.add('error');
        iconElement.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M6 6l8 8M6 14l8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;
    }
}

function showCompleteScreenProgressive() {
    showScreen('complete');

    // Initialize transcriptions with loading state
    let transcriptionsHtml = '';
    for (let i = 1; i <= state.totalQuestions; i++) {
        const question = window.QUESTIONS[i - 1];
        transcriptionsHtml += `
            <div class="transcription-item" id="transcription-${i}">
                <h4>${question.title}</h4>
                <p class="transcription-text">
                    <span class="spinner small"></span> Processing...
                </p>
            </div>
        `;
    }
    elements.transcriptionsSummary.innerHTML = transcriptionsHtml;

    // Show analysis loading state
    elements.analysisSummary.innerHTML = '<p><span class="spinner small"></span> Waiting for transcriptions to complete...</p>';
}

function updateTranscriptionDisplay(questionId, transcription, isError = false) {
    const element = document.getElementById(`transcription-${questionId}`);
    if (!element) return;

    const textElement = element.querySelector('.transcription-text');
    
    if (isError) {
        textElement.innerHTML = '<em style="color: #d32f2f;">Transcription failed</em>';
    } else if (transcription === null || transcription === undefined) {
        textElement.innerHTML = '<em>Transcription not available</em>';
    } else if (transcription === '') {
        textElement.innerHTML = '<em>(No speech detected in recording)</em>';
    } else {
        textElement.textContent = transcription;
    }
}

function showAnalysisLoading() {
    elements.analysisSummary.innerHTML = '<p><span class="spinner small"></span> Analyzing your symptoms...</p>';
}

function updateAnalysisDisplay(analysis, isError = false) {
    console.log('[DEBUG] Analysis received:', analysis);
    
    if (isError || !analysis) {
        elements.analysisSummary.innerHTML = '<p>Analysis could not be completed. Our team will review your responses manually.</p>';
        return;
    }

    let analysisHtml = '';

    // Matched symptom category (show only first one)
    if (analysis.matched_categories && analysis.matched_categories.length > 0) {
        const match = analysis.matched_categories[0]; // Only show first category
        analysisHtml += `
            <div class="symptom-category-card">
                <div class="category-label">Symptom Category</div>
                <div class="category-name">${match.category_name}</div>
            </div>
        `;
    }

    // Clinical notes
    if (analysis.clinical_notes) {
        analysisHtml += `
            <div class="analysis-section">
                <h4>Notes for Your Care Team</h4>
                <p>${analysis.clinical_notes}</p>
            </div>
        `;
    }

    // If no matched categories, show a message
    if (!analysisHtml) {
        analysisHtml = '<p>Analysis complete. Our clinical team will review your responses.</p>';
    }

    elements.analysisSummary.innerHTML = analysisHtml;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
