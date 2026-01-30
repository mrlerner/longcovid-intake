import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24).hex())
    CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
    CLAUDE_MODEL = os.environ.get('CLAUDE_MODEL', 'claude-sonnet-4-20250514')

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_VIDEO_DURATION = 180  # seconds
    MIN_VIDEO_DURATION = 5    # seconds
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

    CLINIC_NAME = "University of Cascadia Long-COVID Clinic"

    QUESTIONS = [
        {
            "id": 1,
            "title": "Your Main Concerns",
            "text": "What are the top three things you'd most like help with right now? Please describe the symptoms or problems that matter most to you today.",
            "suggested_duration": 60
        },
        {
            "id": 2,
            "title": "Timeline",
            "text": "How long have you been experiencing these symptoms? You can give an approximate timeline (for example: weeks, months, or since a specific illness or date).",
            "suggested_duration": 45
        },
        {
            "id": 3,
            "title": "Daily Impact",
            "text": "How are these symptoms affecting your day-to-day life right now? Tell us what you struggle to do or can no longer do—such as work or school, physical activity, sleep, thinking or memory, or emotional well-being.",
            "suggested_duration": 60
        }
    ]

    SYMPTOM_CATEGORIES = [
        {
            "id": "energy_crash",
            "name": "Low Energy & Post-Exertion Crashes",
            "description": "Running out of energy quickly and feeling worse after physical or mental effort."
        },
        {
            "id": "orthostatic_intolerance",
            "name": "Dizziness, Heart Racing & Standing Problems",
            "description": "Feeling lightheaded, dizzy, or unwell when standing or being upright."
        },
        {
            "id": "brain_fog",
            "name": "Brain Fog & Mental Fatigue",
            "description": "Difficulty thinking clearly, focusing, remembering, or processing information."
        },
        {
            "id": "sleep_dysregulation",
            "name": "Sleep That Doesn't Restore Me",
            "description": "Trouble sleeping or waking up feeling unrefreshed despite adequate sleep time."
        },
        {
            "id": "breathlessness",
            "name": "Shortness of Breath & Air Hunger",
            "description": "Breathing feels difficult, shallow, or unsatisfying, at rest or with activity."
        },
        {
            "id": "chest_heart",
            "name": "Chest Discomfort & Heart Sensations",
            "description": "Chest pain, tightness, palpitations, or unusual awareness of heartbeat."
        },
        {
            "id": "headache_migraine",
            "name": "Headaches & Migraine-Like Symptoms",
            "description": "Frequent headaches, pressure, migraines, or sensitivity to light and sound."
        },
        {
            "id": "musculoskeletal_pain",
            "name": "Body Pain, Aches & Muscle Weakness",
            "description": "Widespread pain, soreness, stiffness, or feelings of physical weakness."
        },
        {
            "id": "neuropathy",
            "name": "Tingling, Burning & Nerve Sensations",
            "description": "Numbness, tingling, burning, buzzing, or other unusual nerve sensations."
        },
        {
            "id": "gastrointestinal",
            "name": "Stomach, Digestion & Food Sensitivity Issues",
            "description": "Digestive problems such as nausea, bloating, diarrhea, constipation, or food reactions."
        },
        {
            "id": "ent_sensory",
            "name": "Smell, Taste & Ear–Nose–Throat Changes",
            "description": "Changes to smell or taste, sinus issues, ear pressure, or tinnitus."
        },
        {
            "id": "temperature_flares",
            "name": "Temperature Sensitivity & Flu-Like Flares",
            "description": "Feeling unusually hot or cold, sweating, chills, or flu-like sensations without infection."
        },
        {
            "id": "reactivity",
            "name": "Allergy-Like Reactions & Body Over-Reactivity",
            "description": "Strong reactions to foods, smells, environments, or medications."
        },
        {
            "id": "mood_emotional",
            "name": "Mood Changes, Anxiety & Emotional Swings",
            "description": "Anxiety, depression, irritability, or emotional changes that feel physically driven."
        },
        {
            "id": "genitourinary",
            "name": "Bladder, Sexual & Pelvic Changes",
            "description": "Changes in bladder function, pelvic discomfort, or sexual health."
        },
        {
            "id": "multisystem",
            "name": "Multiple Systems & Relapsing Symptoms",
            "description": "Many symptoms across the body that flare, improve, and return over time."
        }
    ]
