import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Web Application configuration
PORT = int(os.getenv("PORT", "8080"))

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Firebase configuration
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

def is_gemini_configured() -> bool:
    """Check if Gemini API is ready for usage."""
    return bool(GEMINI_API_KEY)

def is_firestore_configured() -> bool:
    """Check if Firestore can be initialized."""
    # Firestore can initialize if GOOGLE_APPLICATION_CREDENTIALS is set,
    # or if we are running inside Google Cloud environment (determined by env vars or ADC)
    return bool(GOOGLE_APPLICATION_CREDENTIALS) or bool(os.getenv("K_SERVICE")) or bool(FIREBASE_PROJECT_ID)
